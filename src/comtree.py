import math

class CommunityTree:
    """Semantic Communty Tree"""
    global_cowordnet = None
    global_docs = None
    global_community_detection = None
    def __init__(self, wordnet, comid, doc_num=0):
        self._wordnet = wordnet
        self._children = list()
        self.comid = comid
        self.active = True
        self.proccessed = False
        self.doc_num = doc_num

    def get_comid(self):
        return self.comid

    def iterdoc(self):
        for doc in CommunityTree.global_docs:
            if doc.belongto_commmunity(self.comid):
                yield doc

    #def getLeafCommunities():
        

    def should_split(self):
        return not self.proccessed and self._wordnet.vcount() > 50 and self.doc_num > 50

    def split(self):
        if self.should_split():
            flag = self.make_children()
            if flag:
                self.map_doc_to_children()
                self.rebuild_wordnet()
            self.proccessed = True

    def make_children(self):
        wid_comus = CommunityTree.global_community_detection.detect(self._wordnet)
        if len(wid_comus)<=1:
            self.active = False
            return False
        #com_docset = self.mapdoc(word_comus)
        print 'Community %d generage %d children' % (self.comid, len(wid_comus))
        for i in range(0, len(wid_comus)):
            chcid = self.comid*10 + i     # bug when size of sub-community great than 10
            subg = self._wordnet.subgraph(wid_comus[i])
            subg.vs['weight'] = subg.pagerank()
            subcom = CommunityTree(subg, chcid)
            self._children.append(subcom)
        return True

    def map_doc_to_children(self):
        """ map documents to communities """
        if self.proccessed: return
        for doc in self.iterdoc():
            doc.remove_community(self.get_comid()) # document remove from current community
            corrChildren = self.correlative_commuities(doc)
            for child in corrChildren:
                doc.add_community(child.get_comid())
                child.doc_num += 1
        # todo: small communities and merge communities

    def rebuild_wordnet(self, min_coocur=2, min_weight=1e-3):
        wn = self._wordnet
        gwn = CommunityTree.global_cowordnet
        for w1,w2,co,wg in self.wordpair_weight(self.iterdoc(), min_coocur, min_weight):
            try: 
                wn.vs.find(name=w1)
            except ValueError:
                wn.add_vertex(w1)
            try: 
                wn.vs.find(name=w2)
            except ValueError:
                wn.add_vertex(w2)
            wn[w1,w2] = (wn[w1,w2]+wg) * co / gwn[w1,w2]
            
        wn.vs['weight'] = wn.vs.pagerank()
    

    def correlative_commuities(self, doc, multi = True, min_correl = 0):
        correls = []
        m,m_child = min_correl, -1
        for child in self._children:
            v = self.correlativeValue(doc,child._wordnet)
            correls.append(v)
            if v>m: m, m_idx=v, child; 

        if m_idx == -1: return [] 
        if not multi:
            return [m_child, ] 
        else:
            # normalization
            s = sum(correls)
            correls = [v/s for v in correls]
            m = max(correls)
            ret_coms = []
            for i, v in enumerate(correls):
                if (m-v)/m <= 0.2:
                    ret_coms.append(self._children[i])
 
            return ret_coms      
        

    @classmethod
    def correlativeValue(cls, doc, wordnet):
        sim = 0.0
        asso = 0.0
        for word, weight in doc:
            try:
                v = wordnet.vs.find(name=word)
                sim += v['weight'] * weight
                
                for e in wordnet.es.select(_source=v.index):
                    asso += weight * wordnet[e.target]['weight'] * e['weight']
            except ValueError:
                pass
        return sim+asso

    @classmethod
    def wordpair_weight(cls,doc_seq, min_coour=2, min_weight=1e-3):
        wordlist_dict = dict() # word: adjacent word sequence
        for doc in doc_seq:
            kws = list(doc.iterkeys())
            for i in range(0,len(kws)):
                adjlist = None
                try:
                    adjlist = wordlist_dict[kws[i]]
                    adjlist.inc_df()
                except:
                    adjlist = WordAdjList()
                    wordlist_dict[kws[i]] = adjlist
                for j in range(0, len(kws)):
                    if i != j:
                        adjlist.add_word(kws[j])
        for source, adjlist in  wordlist_dict.iteritems():
            for target,co_num in adjlist.iteritems():
                if source < target and co_num >= min_coour:
                    df1,df2 = adjlist.get_df(), wordlist_dict[target].get_df()
                    weight = co_num/math.sqrt(df1 * df2)
                    if weight > min_weight:
                        yield (source, target,co_num, weight)

    @classmethod
    def unclassified_docs(cls):
        for doc in cls.global_docs:
            if not doc.is_classifed():
                yield doc
          
class Document:
    """ represent a document """
    def __init__(self, docid, word_dict):
        self.docid = docid
        self.comids = set()
        self.word_dict = word_dict
    
    def belongto_commmunity(self, comid):
        return comid in self.comids
    def is_classifed(self):
        return not self.comids
    def add_community(self, comid):
        self.comids.add(comid)
    def remove_community(self, comid):
        self.comids.remove(comid)

    def __iter__(self):
        return self.word_dict.iteritems()

    def iterwords(self):
        return self.word_dict.iterkeys()

    def __getitem__(self, word):
        return self.word_dict[word]

    def __hash__(self):
        return self.docid
    
    def __eq__(self, other):
        return self.docid == other.docid

    def __cmp__(self, other):
        return self.docid - other.docid


class WordAdjList:
    def __init__(self):
        self.adj_words = dict()
        self.df = 1
    
    def add_word(self, word):
        try:
            self.adj_words[word]+=1
        except KeyError:
            self.adj_words[word]=1

    def __iter__(self):
        return self.adj_words.iteritems()

    def inc_df(self):
        self.df += 1

    def get_df(self):
        return self.df

