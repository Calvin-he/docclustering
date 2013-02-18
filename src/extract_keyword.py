import sqlite3
import dbutils
import xhe_utils as utils
import sys
from wordweight import WordWeightEvaluation

def init_db(db_path):  
    db_con = sqlite3.connect(db_path)

    db_con.executescript('''drop table if exists word;
create table if not exists word  (
wid integer,
word text unique not null,
org_words text, 
pos text,
t_df integer default 0,
c_df integer default 0);
''');

    return db_con

def word_preproc(dbcon, commonwordfile='../data/commonword'):
    """ statistic word document frequency,remove high word with high DF"""
    noun_dict,verb_dict = dict(),dict()
    commonword_set = load_commonword(commonwordfile)
    for r in dbutils.iterRec(dbcon,'document', 'title content'):
        wordset  = set(' '.join((r[0],r[1])).split())
        for wt in wordset:
            w,t = wt.split('/')
            if w in commonword_set: continue
            if t=='n':
                try:
                    noun_dict[w]+=1
                except KeyError:
                    noun_dict[w]=1
            else: #t=='v'
                try:
                    verb_dict[w]+=1
                except KeyError:
                    verb_dict[w]=1
    for w in noun_dict.keys():
        if w in verb_dict:
            noun_dict[w]+=verb_dict[w]
            del verb_dict[w]

    # sort by df in decending order
    noun_list = noun_dict.items()
    noun_list.sort(cmp=lambda l,r:r[1]-l[1])
    # remove high df word
    #start = int(0.003*len(noun_list))
    #noun_list = noun_list[start:]
    dbcon.executemany("insert into word(word,c_df,pos) values(?,?,'n')", noun_list)

    verb_list = verb_dict.items()
    verb_list.sort(cmp=lambda l,r:r[1]-l[1])
    #remove high df word
    #start = int(0.005*len(verb_list))
    #verb_list = verb_list[start:]
    dbcon.executemany("insert into word(word,c_df,pos) values(?,?,'v')", verb_list)

    dbcon.commit()

def load_commonword(filename, coding='utf-8'):
    wordset = set()
    f = open(filename,'r')
    wordset = frozenset(f.read().decode(coding).split())
    f.close()
    return wordset

def load_wordset(dbcon):
    wordset = set()
    for r in  dbutils.iterRec(dbcon,'word', 'word'):
        wordset.add(r[0])
    return frozenset(wordset)

def title_keyword(dbcon):
    print 'extrating keyword from title...'
    doc_num = dbutils.countOfRecs(dbcon, 'document')

    wordset = load_wordset(dbcon)
    cnt = 0
    for r in dbutils.iterRec(dbcon, 'document', 'docid title'):
        twords = set()
        for wt in r[1].split(' '):
            w = wt.split('/')[0]
            if w in wordset:
                twords.add(w)
        widstr = ' '.join(twords)

        dbutils.updateByPK(dbcon, 'document', {'kw_title':widstr}, {'docid':r[0]})
        
        cnt += 1
        if cnt%50==0:
            utils.updateProgress(cnt,doc_num)
        
    print ''
    dbcon.commit()


def title_df(dbcon):
    print 'statistic word document frequency...'
    doc_num = dbutils.countOfRecs(dbcon, 'document')  
    cnt = 0
    
    for r in dbutils.iterRec(dbcon,'document', 'kw_title'):
        title_set = set(r[0].split())
        for w in title_set:
            df_r = dbutils.queryOneRec(dbcon, 'word', 't_df', 'word=?', (w,))
            assert df_r != None, "'%s' in Document %d except" % (w,r[2])
            dbutils.updateByPK(dbcon, 'word', {'t_df':df_r[0]+1}, {'word':w})

        cnt += 1
        if cnt%50 == 0:
            utils.updateProgress(cnt,doc_num)
    print ''
    dbcon.commit()


def content_keyword(dbcon):
    print 'extracting keyword from content...'
    doc_num = dbutils.countOfRecs(dbcon, 'document')
    wordset = load_wordset(dbcon)
    cnt = 0
    eluate = WordWeightEvaluation(30)
    for r in dbutils.iterRec(dbcon, 'document','docid title content'):
        word_weight_list = eluate.extract_kw(r[1],r[2])
        wordwstr = ' '.join(['%s/%.7f' % idw for idw in word_weight_list])
        dbutils.updateByPK(dbcon, 'document', {'kw_content':wordwstr}, {'docid':r[0]})
         
        cnt += 1
        if cnt%20==0:
            utils.updateProgress(cnt,doc_num)
        
    print ''
    eluate.close()
    dbcon.commit()

def topic_keyword(dbcon):
    dbcon.execute("create table if not exists topic (name text unique not null, doc_num integer default 0, keyword text)")
    cur = dbcon.execute('select cats, count(docid) from document group by cats')
    for r in cur: 
        kwset = dict()
        cur2 = dbcon.execute('select kw_title from document where cats=?', (r[0],))
        for kr in cur2:
            for w in kr[0].split():
                try:
                    kwset[w] += 1
                except KeyError:
                    kwset[w] = 1

        kw_str = ' '.join([w for w,f in kwset.iteritems() if f>1])
        dbutils.insert(dbcon, 'topic', {'name':r[0], 'doc_num':r[1], 'keyword':kw_str})
    dbcon.commit()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dbfile', help='the path of dbfile')
    arg = parser.parse_args()
    db_path = arg.dbfile
    dbcon = init_db(db_path)
    
    word_preproc(dbcon)
    title_keyword(dbcon)
    title_df(dbcon)
    content_keyword(dbcon)
    topic_keyword(dbcon)
    dbcon.close()

if __name__=='__main__':
    main()

