import wordnet
import scp
import dbutils

def load_doc_labels(dbfile):
    labels = []
    dbcon = dbutils.connect_db(dbfile)
    cur = dbcon.execute("select t.rowid from document d join topic t on d.cats=t.name")
    labels = [r[0] for r in cur]
    dbcon.close()
    return labels

def load_topic_keyword(dbpath):
    import sqlite3
    dbcon = sqlite3.connect(dbpath)
    topic_kw = []
    for r in dbcon.execute('select keyword from topic'):
        topic_kw.append(frozenset(r[0].split()))
    dbcon.close()
    return topic_kw

def compareWordCluster(wclusters, realwclusters):
    """(real)wclusters is a sequence of word set """
    if not wclusters: return (0.0,0.0)
    #print wclusters
    # static precision rate
    prec_list = []
    for wc in wclusters:
        max_clen = 0
        for rwc in realwclusters:
            clen = len(wc & rwc)
            if clen > max_clen:
                max_clen = clen
        prec_list.append(max_clen/float(len(wc)))
    prec_rate = float(sum(prec_list))/len(prec_list)
    #statics call rate
    wset, rcset = set(), set()
    for wc in wclusters: wset.update(wc)
    for rwc in realwclusters: rcset.update(rwc)
    call_rate = len(wset & rcset)/float(len(rcset))

    return (prec_rate,call_rate)

def get_communities_scp(topicfile, graph=None, outfile=None, k=3, min_nodes=10):
    if graph == None:
        graph = wordnet.loadTitleWordnet(topicfile, min_coocur=1)
    coms = scp.communities_scp(graph,k,min_nodes)
    coms = scp.comuid2name(graph, coms)
    
    if outfile != None:
        f = open(outfile, 'w')
        for i in range(0,len(coms)):
            s = str(i+1)+ u":" + u' '.join(coms[i])+'\r\n'
            f.write(s.encode('gb18030'))
        f.close()
    
    return coms
    

def cmp_community_scp(topicfile, graph=None, coms=None, k=3, min_nodes=10):
    if graph == None:
        graph = wordnet.loadTitleWordnet(topicfile, min_coocur=1)
    
    coms = scp.communities_scp(graph,k,min_nodes)
    coms = scp.comuid2name(graph, coms)
    
    realcoms = load_topic_keyword(topicfile)
    return compareWordCluster(coms, realcoms)

def test():
    dbfile = '../data/cn-topic.db'
    from CommunityBuilder import CommunityBuilder
    cb = CommunityBuilder(dbfile)
    g = cb.load_title_wordnet(2)

    ks = [3,4,5,6,7]
    kcomslist = [get_communities_scp(dbfile,g,k=k) for k in ks]
    print 'sizes of communities:'
    i = 3
    for coms in kcomslist:
        sizes = [len(c) for c in coms]
        print 'k=%d: %s' % (i, str(sizes)) 
        i+=1

    print 'accurate of communties:'
    i = 3
    real_coms = load_topic_keyword(dbfile)
    for coms in kcomslist:
        v = compareWordCluster(coms, real_coms)
        print 'k=%d: %s' % (i, str(v))
        i+=1



def cmp_doc_clusters(predicted, labels, method='rand'):
    from sklearn import metrics
    if method == 'rand':
        #he Rand Index computes a similarity measure between two clusterings by considering all pairs of samples and counting pairs that are assigned in the same or different clusters in the predicted and true clusterings.
        return metrics.adjusted_rand_score(labels,predicted)
    elif method == 'nmi':
        return metrics.adjusted_mutual_info_score(labels,predicted)
    elif method == 'v-measure':
        #The V-Measure is the hormonic mean between homogeneity and completeness:v = 2 * (homogeneity * completeness) / (homogeneity + completeness)
        return metrics.v_measure_score(labels, predicted)
    elif method == 'homo':
        #A clustering result satisfies homogeneity if all of its clusters contain only data points which are members of a single class.
        return metrics.homogeneity_score(labels, predicted)
    elif method == 'complete':
        #A clustering result satisfies completeness if all the data points that are members of a given class are elements of the same cluster.
        return metrics.completeness_score(labels, predicted)
    elif method=='f-measure':
        return fmeasure_metrics(predicted,labels)[2]
    elif method=='prec':
        return fmeasure_metrics(predicted,labels)[0]
    elif method=='call':
        return fmeasure_metrics(predicted,labels)[1]
        raise NotImplementedError


def fmeasure_metrics(predicted, labels):
    table = [0,0,0,0]
    n = len(predicted)
    for i in range(0,n):
        for j in range(i+1,n):
            t = 0 if predicted[i] == predicted[j] else 1
            p = 0 if labels[i] == labels[j] else 1
            table[t*2+p] += 1
    p = table[0]/float(table[0] + table[1])
    r = table[0]/float(table[0] + table[2])
    fm =  2.0*table[0] /(2.0*table[0] + table[1] + table[2])
    return (p,r,fm)              


def purity_metrics(predicted, labels):
    v1 = set(predicted)
    v2 = set(labeles)
    cp,cl = dict(),dict()
    for v in v1: cp[v] = set()
    for v in v2: cl[v] = set()
    for i,c in enumerate(predicted):
        cp[c].add(i)
    for i,c in enumerate(labels):
        cl[c].add(i)

    



