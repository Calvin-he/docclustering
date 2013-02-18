import sqlite3
import sys, itertools
import math
import dbutils

def init_db(db_path):
    print 'initizing database...'
    db_con = sqlite3.connect(db_path)
    
    db_con.executescript('''create table if not exists t_wordpair (
 word1 text not null, 
 word2 text not null,
 coocur_num integer default 0,
 weight number default 0,
 rweight number default 0);
 create unique index u_idx_t_wordpair on t_wordpair
 (word1, word2)''')
    return db_con

def title_wordpair(db_con):
    print 'statistic word co-ocurence from title...'

    codict,dfdict=dict(),dict()
    cnt = 0
    for r in dbutils.iterRec(db_con, 'document','kw_title'):
        words = r[0].split(' ')
        for wp in itertools.combinations(words, 2):
            if wp[0]>wp[1]: wp = (wp[1],wp[0])
            codict[wp] = (codict[wp]+1) if wp in codict else 1
        for w  in words:
            dfdict[w] = (dfdict[w]+1) if w in dfdict else 1

        cnt+=1
    print 'doc num: %d' % cnt
    print 'number of wordpair in title_wordpair: %d' % len(codict)
    cnt = 0
    for wp,co in codict.iteritems():
        weight = co/math.sqrt(dfdict[wp[0]]*dfdict[wp[1]])
        if co>=2 and weight>1e-3:
            cnt += 1
        dbutils.insert(db_con, 't_wordpair', {'word1':wp[0], 'word2':wp[1], 'coocur_num':co, 'weight':weight})
    print 'number of edges '+str(cnt)
    db_con.commit()        

# def title_wordpair_weight(db_con, max_df=100000):
#     print "computing word pairs' weight from title...."
#     pair_num = dbutils.countOfRecs(db_con,'t_wordpair')  
#     cnt = 0

#     for r in dbutils.iterRec(db_con, 't_wordpair', 'word1 word2 coocur_num'):
#         w1,w2 = (r[0],r[1]) if r[0]<r[1] else (r[1],r[0]) 
#         cur2 = db_con.execute('select t_df from word where word=? or word=?', (w1,w2)) 
#         df1 = cur2.next()[0]
#         df2 = cur2.next()[0]
#         if df1 <= max_df and df2 <= max_df:
#             gmean = math.sqrt(df1*df2)
#             (weight, rweight) = (r[2]/gmean, r[2]/gmean)
#             db_con.execute('update t_wordpair set weight=?, rweight=? where word1=? and word2=?', (weight, rweight, w1, w2))

#         cnt += 1
#         if cnt%100 == 0:
#            utils.updateProgress(cnt,pair_num)
#     print ''
#     db_con.commit()        


# def insert_or_update_coocur(db_con, word_pair):
#     cur = db_con.execute('select coocur_num from t_wordpair where word1=? and word2=?',word_pair)
#     r = cur.fetchone()
#     if r is None:
#         db_con.execute('insert into t_wordpair (word1, word2, coocur_num) values(?,?,?)',
# (word_pair[0], word_pair[1], 1))
#     else:        
#         db_con.execute('update t_wordpair set coocur_num=? where word1=? and word2=?',
# (r[0]+1, word_pair[0], word_pair[1]))
    
#     cur.close()

def main():
    db_path = sys.argv[1]
    db_con = init_db(db_path)
    
    title_wordpair(db_con)
    #title_wordpair_weight(db_con)

    db_con.close()


if __name__  == '__main__':
    main()
