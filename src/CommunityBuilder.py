import os, time
import dbutils
import igraph
import cmpcluster
from comgroup import Community, CommunityGroup, Document
import comdect

class CommunityBuilder:
    def __init__(self, dbfile, logfile=None):
        self.dbfile = dbfile
        self.logfile = logfile
        self._run_time = 0.0

    def build(self, max_depth=5, min_doc_num=10):
        (twn,docs) = self.load_data()
        return self.build_from_data(twn,docs,max_depth,min_doc_num)

    def load_data(self):
        twn = self.load_title_wordnet()
        docs = list(self.iter_document())
        return (twn,docs)
    
    def build_from_data(self,twn,docs,max_depth=5, min_doc_num=15):
        starttime = time.time()
        cowordnet = self.build_global_cowordnet(docs)
        com_dect = comdect.LabelCommunityDetection(min_nodes=20)
        group = CommunityGroup(cowordnet,docs,com_dect)
        real_labels = None
        if self.logfile:
            real_labels = self.load_doc_labels(docs)
            self.resoutput = open(self.logfile,'w')
            self.resoutput.write('NCluster \tAdjusted_Rand \tAdjusted_NMI \tF-Measure \tV-Measure \tprecison \tcall\n')
        depth = 0
        rootcom = Community(twn,group,len(docs))
        group.add_community(rootcom)

        while depth<=max_depth:
            acoms = group.active_coms()
            if not acoms: break
            print 'dividing community'
            for c in acoms:
                children = c.make_children()
                if children:
                    group.remove_community(c)
                    for ch in children:
                        group.add_community(ch)
                  
            acoms = group.active_coms()
            if not acoms: break
 
            uncdocs = group.unclassified_docs()
            print 'Mapping unclassified document into communities'
            Community.map_docs_to_coms(uncdocs, acoms)
            group.remove_null_community(min_doc_num)
            depth += 1
            if self.logfile:
                predicted = group.doc_labels()
                rs = cmp_cluster_result(predicted,len(group),real_labels)
                self.resoutput.write(rs)
            print 'rebuilding wordnet'
            for c in acoms:
                c.rebuild_wordnet()

        self.merge_communities(group, 0.5)
        if self.logfile:
            predicted = group.doc_labels()
            rs = cmp_cluster_result(predicted,len(group),real_labels)
            self.resoutput.write(rs)
            self.resoutput.write('\r\n')
            self.resoutput.write(self.output_keywords(group).encode('utf8'))
        
            self.resoutput.close()
            #os.system('emacs ../doc_clustering_evalution.txt')
        self._run_time = time.time() - starttime
        print 'Elapsed time: %.2fs' % self._run_time
        return group.doc_labels()
   
    def output_keywords(self,group):
        s = ''
        for com in group:
            s += str(com.get_doc_num())+ ": "+ ' '.join(com.top_keywords()) + '\r\n'
        return s

    def merge_communities(self, group, merge_freshold=0.5):
        n = len(group)
        dset = DisjoinSet(n)
        coms = list(iter(group))
        for i in range(0,n-1):
            for j in range(i+1,n):
                sim = Community.similarity(coms[i],coms[j])
                #print 'similarity: %.5f' % sim
                if sim > merge_freshold:
                    dset.union(i,j)
        
        clusters = dset.sets(min_size=2)
        for c in clusters:
            group.merge_communities([coms[i] for i in c])

    def load_title_wordnet(self,min_coocur=2, min_weight=1e-3):
        titleiter = Community.wordpair_weight(self.iter_title_words(), min_coocur, min_weight)
        elist = []
        for w1,w2,co,weight in titleiter:
            elist.append({'source':w1, 'target':w2, 'weight':weight})
        return igraph.Graph.DictList(vertices=None, edges=elist)

    def iter_title_words(self):
        dbcon = dbutils.connect_db(self.dbfile)
        for r in dbutils.iterRec(dbcon,'document','kw_title'):
            yield Document(0, {w:0 for w in r[0].split(' ')})

        dbcon.close()

    def iter_document(self):
        dbcon = dbutils.connect_db(self.dbfile)
        for r in dbutils.iterRec(dbcon,'document','docid kw_content'):
            word_dict = {}
            for ww in r[1].split():
                s = ww.split('/')
                word_dict[s[0]] = float(s[1])
            doc = Document(r[0], word_dict)
            yield doc

        dbcon.close()


    def build_global_cowordnet(self, docs, min_coocur=2):
        dociter = Community.wordpair_weight(docs, min_coocur,0)
        # import itertools
        # co_dict = dict()
        # for words in docs:
        #     for wp in itertools.combinations(words,2):
        #         if wp[1]>wp[0]: wp = (wp[1],wp[0])
        #         try:
        #             co_dict[wp] += 1
        #         except: 
        #             co_dict[wp] = 1

        def dict2list(docs):
           for w1,w2,co,weight in docs:
               yield {'source':w1, 'target':w2, 'weight':co}

        return igraph.Graph.DictList(vertices=None, edges=dict2list(dociter))
    

    def load_doc_labels(self, docs):
        labels = []
        dbcon = dbutils.connect_db(self.dbfile)
        for d in docs:
            cur = dbcon.execute('select t.rowid from document d join topic t on d.cats=t.name and d.docid=?', (d.get_docid(),))
            labels.append(cur.fetchone()[0])
            cur.close()
        dbcon.close()
        return labels
        
    def outputCommunities(self, com_group, filename):
        f = open(filename, 'w')
        f.write(str(com_group))
        f.close()
    
        # for com in group:
        #     s = ' '.join[str(d.get_docid()) for d in com.iterdoc()]
        #     f.write(str(com.get_com_id) + ': ')
        #     f.write(s)
        #     f.write('\r\n')

        # f.close()

class DisjoinSet:
    def __init__(self,n):
        self.parent = range(0,n)
        
    def find(self, i):
        root = i
        elems = []
        if root != self.parent[root]:
            root = self.parent[root]
            elems.append(root)
        for e in elems:
            self.parent[e] = root
        return root

    def union(self, i,j):
        ri = self.find(i)
        rj = self.find(j)
        if ri != rj:
            self.parent[i] = rj

    def sets(self, min_size=1):
        clusters = [[] for i in range(0,len(self.parent))]
        for i in range(0,len(self.parent)):
            root = self.find(i)
            clusters[root].append(i)
        return [li for li in clusters if len(li)>=min_size]

def cmp_cluster_result(predicted,ncluster,real_labels):
    adjr = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'rand')
    nmi = cmpcluster.cmp_doc_clusters(predicted,real_labels,'nmi')
    fm = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'f-measure')
    vm = cmpcluster.cmp_doc_clusters(predicted,real_labels, 'v-measure')
    prec = cmpcluster.cmp_doc_clusters(predicted,real_labels,'prec')
    call = cmpcluster.cmp_doc_clusters(predicted,real_labels,'call')
    #homo = cmpcluster.cmp_doc_clusters(predicted, real_labels,'homo')
    #compt = cmpcluster.cmp_doc_clusters(predicted, real_labels, 'complete')
    s = '%d \t%.3f \t%.3f \t%.3f \t%.3f \t%.3f \t%.3f\n' % (ncluster, adjr, nmi, fm, vm, prec, call)
    return s
        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dbfile', help='the sqlite file to proccessed')
    parser.add_argument('-l', '--logfile', help='store the result to logfile')
    args = parser.parse_args()
    cb = CommunityBuilder(args.dbfile, args.logfile)
    cb.build(5)
    if args.logfile:
        os.system('emacs ../result/doc_clustering_evalution.txt')







