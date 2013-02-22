# --*-- encoding=utf-8
from worddf import WordDF
import math,heapq

class WordWeightEvaluation:
    def __init__(self, kw_num=20, worddfdir = '../data/worddf'):
        self.worddf = WordDF('r', worddfdir)
        self.docsize = self.worddf.doc_size()
        self.kwnum = kw_num

    def close(self):
        self.worddf.close()

    def extract_kw(self, title, content, seg_text=False):
        """ 
        给出一篇文本的标题和内容，输出关键词及相应权重的列表。
        如果seg_text为True,说明还没有分过词，需要分词处理
        """
        if seg_text:
            if title:
                title = self.seg_text(title)
            content = self.seg_text(content)

        word_dict = dict()
        if title:
            self.__stats_tf(word_dict, title, coef=2.0)
        self.__stats_tf(word_dict, content, coef=1.0)

        #sum_tf = sum(word_dict.itervalues())
        for w,v in word_dict.iteritems():
            df = self.worddf.df(w) + 1.0
            idf = math.log(self.docsize/df, 2)
            ntf = v * idf
            word_dict[w] = ntf
        wwlist = heapq.nlargest(self.kwnum, word_dict.iteritems(), key=lambda x:x[1])
        sumw = sum([ww[1] for ww in wwlist])
        result = []
        for word,weight in wwlist:
            weight = weight / sumw
            result.append((word,weight))
        return result

    def __stats_tf(self, word_dict, wordtagstr, coef=1.0):
        for wotstr in wordtagstr.split():
            wot = wotstr.split('/')
            weight = 0
            if wot[1] == 'n':
                weight += 2
            elif wot[1] == 'v':
                weight += 1
            else: continue
            try:
                word_dict[wot[0]] += coef*weight
            except:
                word_dict[wot[0]] = coef*weight
        

    def seg_text(self, text):
        raise NotImplementedError()
