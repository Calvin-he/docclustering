import dbutils
import cmpcluster
import os
import time
import Pycluster

def transfer_data_file(dbfile, outputfile):
    con = dbutils.connect_db(dbfile)
    words = dict()
    for d in dbutils.iterRec(con, 'document','kw_content'):
        for ww in d[0].split(' '):
            word,weight = ww.split('/')
            words[word] = (words[word]+1) if word in words else 1
    # for w in words.keys():
    #     if words[w] <= 1:
    #         del words[w]
    # print 'count of words: %d' % len(words)
                
    out = open(outputfile, 'w')
    rang = range(0,len(words))
    out.write('\t'.join(words.iterkeys()).encode('utf8'))
    out.write('\r\n')
    out.write('\t'.join(['c' for i in rang]))
    out.write('\r\n\r\n')

    for d in dbutils.iterRec(con, 'document', 'kw_content'):
        for w in words: words[w] = 0.0
        for ww in d[0].split(' '):
            word,weight = ww.split('/')
            if word in words:
                words[word]=float(weight)
        out.write('\t'.join([str(v) for v in words.itervalues()]))
        out.write('\r\n')

    out.close()
    con.close()

def load_data_to_array(data_file):
    import numpy as np
    data = np.loadtxt(data_file, dtype='float', delimiter='\t', skiprows=3)
    return data

def out_result_header():
    return 'NCluster \tAdjusted_Rand \tAdjusted_NMI \tF-Measure  \tV-Measure\r\n'

def out_result(predicted,k, real_labels):
    adjr = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'rand')
    nmi = cmpcluster.cmp_doc_clusters(predicted,real_labels,'nmi')
    fm = cmpcluster.cmp_doc_clusters(predicted,real_labels,'f-measure')
    vm = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'v-measure')
    s = '%d \t%.3f \t%.3f \t%.3f \t%.3f\r\n' % (k, adjr, nmi, fm, vm)
    return s
    

def kmeans_cluster_test(data, real_labels, outputfile=None):
    start = time.time()

    ks = range(8,15)
    if outputfile != None:
        f = open(outputfile,'w')
        f.write(out_result_header())
    for k in ks:
        print 'running kmeans when k=%d' % k
        predicted = Pycluster.kcluster(data,k)[0].tolist()
        if outputfile != None:
            f.write(out_result(predicted,k, real_labels))
        
    f.close()
    elasped = time.time() - start
    print 'Average time: %.3f' % (elasped/float(len(ks)))


def tree_cluster_test(data,real_labels, outputfile = None):
    start = time.time()
    tree = Pycluster.treecluster(data, method='m')    

    ks = range(25,50,1)
    if outputfile != None:
        f = open(outputfile,'w')
        f.write(out_result_header())
    for k in ks:
        print 'hierachical clustering whn k=%d' % k
        predicted = tree.cut(k).tolist()
        if outputfile != None:
            f.write(out_result(predicted,k, real_labels))

    elasped = time.time() - start
    print 'hierarchical clustering time: %.3f' % (elasped/float(len(ks)))

def som_cluster_test(data,real_labels, outputfile = None):
    if outputfile != None:
        f = open(outputfile,'w')
        f.write(out_result_header())

    start = time.time()
    ks = range(6,40)
    for k in ks:
        print 'som clustering when k=%d' % k
        predicted = Pycluster.somcluster(data,nxgrid=k,nygrid=1, niter=5, dist='u')[0]
        predicted = [xy[0] for xy in predicted.tolist()]
        cata = tuple(set(predicted))
        for i in range(0,len(predicted)):
            predicted[i]=cata.index(predicted[i])
        if outputfile != None:
            f.write(out_result(predicted, k, real_labels))

    elasped = time.time() - start
    print 'som clustering time: %.3f' % (elasped/float(len(ks)))

def dbscan_cluster_test(data, real_labels, outputfile=None):
    from sklearn import cluster
    start = time.time()
    if outputfile != None:
        f = open(outputfile,'w')
        f.write(out_result_header())
 
    print 'running dbscan'
    db = cluster.DBSCAN(eps=0.1).fit(data)
    predicted = db.labels_
    k = len(set(predicted))
    if outputfile != None:
        f.write(out_result(predicted,k, real_labels))
        
       
    elasped = time.time() - start
    print 'running time: %.3f' % (elasped)

    

def main():
    import sys
    dbfile = sys.argv[1]
    algor = sys.argv[2]
    #dbfile = '../data/topicgj.db'
    s,e = dbfile.rindex('/')+1, dbfile.rindex('.')
    outfile = '../result/%s_orange_fmt.tab' % dbfile[s:e]
    real_labels = cmpcluster.load_doc_labels(dbfile)
    if not os.path.exists(outfile):
        transfer_data_file(dbfile,outfile)
    
    #os.system('emacs '+ outfile)
    
    res_outfile = '../result/%s_cluster_result.txt' % algor
    data = load_data_to_array(outfile)
    if algor == 'kmeans':
        kmeans_cluster_test(data, real_labels, res_outfile)
    elif algor == 'tree':
        tree_cluster_test(data, real_labels, res_outfile)
    elif algor == 'som':
        som_cluster_test(data, real_labels, res_outfile)
    elif algor == 'dbscan':
        dbscan_cluster_test(data,real_labels, res_outfile)
    else:
        raise NotImplementedError
    os.system('emacs '+res_outfile)

if __name__ == '__main__':
    main()
