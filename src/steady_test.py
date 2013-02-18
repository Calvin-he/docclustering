# -*- encoding=utf-8 -*-
"""
稳定性测试实验
"""
import numpy as np
import os
import cmpcluster
from CommunityBuilder import CommunityBuilder
def out_result_header():
    return 'NNoise \tARI \tANMI \tFM  \tVM\n'

def cmp_cluster(predicted, real_labels):
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

def main():
    import preproc_qqtopic
    import extract_keyword
    import worddf
    dbfile = '../data/steady_test.db'
    logsteadyfile = '../result/steady_test.log'
    
    steadyfile = open(logsteadyfile,'w')
    steadyfile.write(out_result_header())
     
    if not os.path.exists(dbfile):
        preproc_qqtopic.load_topiclist(dbfile,'../data/topicgj')
        wdf = worddf.WordDF('c')
        wdf.add_docs_from_db(dbfile)
        wdf.close()

        dbcon = extract_keyword.init_db(dbfile)
        extract_keyword.word_preproc(dbcon)
        extract_keyword.title_keyword(dbcon)
        extract_keyword.title_df(dbcon)
        extract_keyword.content_keyword(dbcon)
        extract_keyword.topic_keyword(dbcon)
        dbcon.close()


    cb = CommunityBuilder(dbfile)
    
    metrics = list()
    c = 50
    real = cmpcluster.load_doc_labels(dbfile)
    print 'steady_test'
    for i in range(c):
        print 'Time %d' % (i+1)
        predicted = cb.build()
        metrics.append(cmp_cluster(predicted,real))
    
    mean,std = mean_std(metrics)
    meanstr = '%.1f \t%.3f \t%.3f \t%.3f \t%.3f\n' % tuple(mean)
    stdstr =  '%.1f \t%.3f \t%.3f \t%.3f \t%.3f\n' % tuple(std)
    steadyfile.write(meanstr)
    steadyfile.write(stdstr)
    steadyfile.close()
    os.system('emacs '+logsteadyfile)

if __name__ == '__main__':
    main()
