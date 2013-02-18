# -*- encoding=utf-8 -*-
"""
抽取样本作噪音分析测试实验
"""
import os,random
from CommunityBuilder import CommunityBuilder
import cmpcluster
import numpy as np

def out_result_header():
    return 'NNoise \tARI \tANMI \tFM  \tVM\n'
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

def sample_docs(num=500, srcdir='../data/noise'):
    sfiles = []

    files = os.listdir(srcdir)
    for f in random.sample(files,num):
        sfiles.append(os.path.join(srcdir,f))
    return sfiles

    
def main():
    import preproc_qqtopic
    import extract_keyword
    #import worddf
    dbfile = '../data/noise_test.db'
    lognoisefile = '../result/noise_test.log'
    
    noisefile = open(lognoisefile,'w')
    noisefile.write(out_result_header())
    rang = xrange(0,250, 60)
    for num in rang:
        files = sample_docs(num)
        if os.path.exists(dbfile):
            os.remove(dbfile)
        
        preproc_qqtopic.load_topiclist(dbfile,'../data/topicgj')
        cnt = preproc_qqtopic.prepro_topic(dbfile,'noise_data',files)
        print 'add number of noise document: %d' % cnt

        # wdf = worddf.WordDF('c')
        # wdf.add_docs_from_db(dbfile)
        # wdf.close()

        dbcon = extract_keyword.init_db(dbfile)
        extract_keyword.word_preproc(dbcon)
        extract_keyword.title_keyword(dbcon)
        extract_keyword.title_df(dbcon)
        extract_keyword.content_keyword(dbcon)
        extract_keyword.topic_keyword(dbcon)
        dbcon.close()
   
        cb = CommunityBuilder(dbfile)
        metrics = list()
        c = 10
        real = cmpcluster.load_doc_labels(dbfile)
        print 'noise_test %d' % num
        for i in range(c):
            predicted = cb.build()
            metrics.append(cmp_cluster(predicted,real))
        mean,std = mean_std(metrics)
        meanstr = '%.1f \t%.3f \t%.3f \t%.3f \t%.3f\n' % tuple(mean)
        stdstr =  '%.1f \t%.3f \t%.3f \t%.3f \t%.3f\n\n' % tuple(std)
        noisefile.write(meanstr)
        noisefile.write(stdstr)
    noisefile.close()
    os.system('emacs '+lognoisefile)
if __name__ == '__main__':
    main()
