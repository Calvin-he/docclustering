# -*- encoding=utf-8 -*-
"""
随机抽选topic实验
"""
import os,random
from CommunityBuilder import CommunityBuilder
import cmpcluster
import numpy as np
import preproc_qqtopic
import extract_keyword2
from wordweight import WordWeightEvaluation
from sys import getfilesystemencoding
def out_result_header():
    return 'NSample \tARI \tANMI \tFM  \tVM\n'
def cmp_cluster(predicted, real_labels):
    predicted = predicted[0:1222]
    real_labels = real_labels[0:1222]
    ncluster = len(set(predicted))
    adjr = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'rand')
    nmi = cmpcluster.cmp_doc_clusters(predicted,real_labels,'nmi')
    fm = cmpcluster.cmp_doc_clusters(predicted,real_labels,'f-measure')
    vm = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'v-measure')
    return [ncluster, adjr,nmi,fm,vm]
    
def mean_std(metrics):
    A = np.array(metrics)
    mean = np.mean(A, axis=0).tolist()
    std = np.std(A,axis=0).tolist()
    return (mean,std)

def sample_topics(num=10, topicdir='../data/alltopicgj'):
    topics = []
    alltopics = os.listdir(topicdir)
    for t in random.sample(alltopics,num):
        t = t.decode(getfilesystemencoding())
        topics.append(os.path.join(topicdir,t))

    return topics

def topics_to_db(topics, dbfile):
    import sqlite3
    if os.path.exists(dbfile): os.remove(dbfile)
    dbcon = preproc_qqtopic.init_db(dbfile)
    for t in topics:
        idx = t.rindex('/')
        if idx == len(t)-1:
            idx = t.rindex('/', 0, idx)
        tname =  t[idx+1:]
        files = os.listdir(t)
        filelist = [os.path.join(t,f) for f in files]
        
        preproc_qqtopic.load_topic(dbcon, tname, filelist)
    dbcon.close()

    evaluator = WordWeightEvaluation(30)
    ke = extract_keyword2.DBKeywordExtractor(dbfile,evaluator)
    ke.init_db()
    ke.content_keyword()
    ke.title_keyword()
    ke.topic_keyword()
    ke.close_db()

    return dbfile

def classify(dbfile, run_num, log_info=None):
    real = cmpcluster.load_doc_labels(dbfile)
    print 'sample_test %d' % run_num
    metrics = list()
    cb = CommunityBuilder(dbfile,log_info)
    for i in range(run_num):
        predicted = cb.build()
        metrics.append(cmp_cluster(predicted,real))
    mean,std = mean_std(metrics)
    return (mean,std)
 


def main():
    #import worddf
    dbfile = '../data/sample_test.db'
    resultlog = '../result/sample_test.log'
    
    samplefile = open(resultlog,'w')
    samplefile.write(out_result_header())
    rang = range(10,11)
    for num in rang:
        topics = sample_topics(num)
        topics_to_db(topics, dbfile)
        mean,std = classify(dbfile, 1)
        meanstr = '%.1f \t%.3f \t%.3f \t%.3f \t%.3f\n' % tuple(mean)
        stdstr =  '%.1f \t%.3f \t%.3f \t%.3f \t%.3f\n\n' % tuple(std)
        samplefile.write(meanstr)
        samplefile.write(stdstr)
    samplefile.close()
    os.system('emacs '+resultlog)
if __name__ == '__main__':
    main()
