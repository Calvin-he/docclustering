### ---*---  encoding=utf-8 ---*---

import comdect
from comgroup import *

class TopicDetection:
    MIN_DOC_NUM=10


    def __init__(self):
        self._co_dict = dict()
        self._df_dict = dict()
        self.topic_group = CommunityGroup() #todo
        self.community_detection = None

    def detect_topic(self):
        wordnet = self.build_wordnet()
        com = Community(wordnet, self.topic_group)
        children = com.make_children()
        if children == None: return
        docs = self.topic_group.unclassified_docs()
        Community.map_docs_to_coms(docs,children)

        #两次分裂，将噪音文本去除
        for com in children:
            #取出少量文本的topic
            if com.get_doc_num() < MIN_DOC_NUM:
                continue
            com.rebuild_wordnet()
            grandchildren=com.make_children()
            if grandchildren == None:
                #子topic不能分裂，则添加到topic_group中去
                self.topic_group.add_community(com)
            else:
                #能分裂的,将少量文本的孙子topic去除。             
                for gcom in grandchildren:
                    if com.get_doc_num() < MIN_DOC_NUM:
                        continue
                    gcom.rebuild_wordnet()
                    self.topic_group.add_community(gcom)
            
    def build_wordnet(self):
        from igraph import Graph
        Graph.TupleList(edges, weights=True)
    
    def __iter_edges

    def next_docs(self, dociter):
        for doc in dociter:
            if not self.classify_doc(doc):
                self.collect_word(doc)
        self.detect_topic()

    def classify_doc(self, doc, threshold=0.8):
        pass

    def collect_word(doc):
        for w in doc.iterwords():
            try:
                self._df_dict[w]+=1
            except:
                self._df_dict[w]=1
        for w1,w2 in doc.iterwordpair():
            try:
                self._co_dict.[(w1,w2)] += 1
            except:
                self._df_dict[(w1,w2)] = 1


class Topic:
    
    def __init__(self, wordnet):
        self._wordnet = wordnet
        self._docnum
    
    
    
    
