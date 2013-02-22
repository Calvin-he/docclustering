import sqlite3
import dbutils
import xhe_utils as utils
import sys
from wordweight import WordWeightEvaluation


class DBKeywordExtractor:
    
    def __init__(self,db_path, weight_evaluator=None):
        self.dbpath = db_path
        self.dbcon = None
        if weight_evaluator:
            self.evaluator = weight_evaluator
        else:
            self.evaluator = WordWeightEvaluation(30,'../data')
            self.evaluator.add_docs_from_db(dbpath)
           
    def init_db(self):
        self.dbcon = sqlite3.connect(self.dbpath)
        
    def close_db(self):
        self.dbcon.close()
        self.evaluator.close()

    def content_keyword(self):
        print 'extracting keyword from content...'
        doc_num = dbutils.countOfRecs(self.dbcon, 'document')
        cnt = 0
        #eluate = WordWeightEvaluation(30)
        for r in dbutils.iterRec(self.dbcon, 'document','docid title content'):
            word_weight_list = self.evaluator.extract_kw(r[1],r[2])
            wordwstr = ' '.join(['%s/%.7f' % idw for idw in word_weight_list])
            dbutils.updateByPK(self.dbcon, 'document', {'kw_content':wordwstr}, {'docid':r[0]})

            cnt += 1
            if cnt%20==0:
                utils.updateProgress(cnt,doc_num)

        print ''
        #eluate.close()
        self.dbcon.commit()

    def title_keyword(self, maxn=5):
        for r in dbutils.iterRec(self.dbcon, 'document', 'docid title kw_content'):
            wordlist = []
            if r[1]:
                for wt in r[1].split():
                    wordlist.append(wt.split('/')[0])
            else:
                #from content keyword
                i = 0
                for ww in r[2].split():
                    wordlist.append(ww.split('/')[0])
                    i += 1
                    if i == maxn: break;
            kwstr = ' '.join(wordlist)    
            dbutils.updateByPK(self.dbcon, 'document', {'kw_title':kwstr}, {'docid':r[0]})
        self.dbcon.commit()
        

    def topic_keyword(self):
        self.dbcon.execute("create table if not exists topic (name text unique not null, doc_num integer default 0, keyword text, weight text)")
        cur = self.dbcon.execute('select cats, count(docid) from document group by cats')
        for r in cur: 
            kwset = dict()
            cur2 = self.dbcon.execute('select kw_title from document where cats=?', (r[0],))
            for kr in cur2:
                for w in kr[0].split():
                    try:
                        kwset[w] += 1
                    except KeyError:
                        kwset[w] = 1

            sum_weight = float(sum(kwset.itervalues()))
            items = kwset.items()
            items.sort(key=lambda x:x[1],reverse=True)
            kw_str = ' '.join([w for w,f in items])
            weight_str = ' '.join([str(f/sum_weight) for w,f in items])
            dbutils.insert(self.dbcon, 'topic', {'name':r[0], 'doc_num':r[1], 'keyword':kw_str, 'weight':weight_str})
        self.dbcon.commit()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dbfile', help='the path of dbfile')
    arg = parser.parse_args()


    extractor = DBKeywordExtractor(arg.dbfile)
    extractor.init_db()
    extractor.content_keyword()
    extractor.title_keyword()
    extractor.topic_keyword()
    extractor.close_db()

if __name__=='__main__':
    main()

