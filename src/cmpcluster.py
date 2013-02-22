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
    for r in dbcon.execute('select keyword,weight from topic'):
        words = r[0].split()
        weights = [float(w) for w in r[1].split()]
        assert len(words)==len(weights)
        topic_kw.append((words,weights))
    dbcon.close()
    return topic_kw

def compare_word_cluster(wclusters, realwclusters):
    """(real)wclusters is a sequence of word set """
    if not wclusters: return 0.0
    #print wclusters
    # static precision rate
    prec_list = []
    
    #sum_words = sum([len(words) for words in wclusters])
    for wc in wclusters:
        max_wmatch,max_nmatch = 0.0,0
        for rwords,rweight in realwclusters:
            wmatch,nmatch = 0.0,0
            for i in xrange(len(rwords)):
                if rwords[i] in wc:
                    wmatch += rweight[i]
                    nmatch += 1
            if wmatch > max_wmatch:
                max_wmatch,max_nmatch = wmatch,nmatch

        prec_list.append(max_wmatch*max_nmatch/len(wc))
    prec_rate = float(sum(prec_list))/len(realwclusters)
  
    return prec_rate

def comuid2name(graph, communities):
    """communities id to name"""
    com_names = []
    for com in communities:
        nameset = set()
        for nid in com:
            nameset.add(graph.vs[nid]['name'])
        com_names.append(nameset)
    return com_names

def test_title_cluster(dbfile = '../data/sample_test.db'):
    from CommunityBuilder import CommunityBuilder
    import comdect
    cb = CommunityBuilder(dbfile)
    g = cb.load_title_wordnet(2)

    detect = comdect.WalkCommunityDetection(min_nodes=15)
    coms = detect.detect(g)
    print len(coms)
    coms = comuid2name(g,coms)
    rwclusters = load_topic_keyword(dbfile)

    purity = compare_word_cluster(coms, rwclusters)
    print purity




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
    v2 = set(labels)
    cp,cl = dict(),dict()
    for v in v1: cp[v] = set()
    for v in v2: cl[v] = set()
    for i,c in enumerate(predicted):
        cp[c].add(i)
    for i,c in enumerate(labels):
        cl[c].add(i)

    



