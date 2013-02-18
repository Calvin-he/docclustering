import nltk
import sqlite3


def seg_text(db_file):
    try:
        conn = sqlite3.connect(db_file)
        conn.text_factory = str
        cur = conn.cursor()
        cur.execute("""CREATE TABLE if not exists seg_words 
(docid integer primary key, 
title text, 
content text)""")
        conn.commit()

        cur1 = conn.cursor()       
        cur1.execute("""SELECT docid, title,content FROM document""")
        count=0c
        records = cur1.fetchadll()
        for r in records:
             title = process_sents(r[1])
             print title
             content = process_text(r[2])
             cur.execute("""INSERT INTO seg_words(docid,title,content) VALUES(?,?,?)""", (r[0],title,content))

             count = count+1
             if count%50 == 0: conn.commit()        
    
        conn.commit()
    except Exception, e:
        print e
    finally:
        conn.close()
    
wordnet_lemm = nltk.WordNetLemmatizer()

def process_sents(sents):
    tokens = nltk.word_tokenize(sents)     
    wordtags = nltk.pos_tag(tokens)
    
    selectedwords = []
    for (word,tag) in wordtags:
        if tag[0] == 'N' and word.isalpha() and not is_stopword(word.lower()):         
            word = wordnet_lemm.lemmatize(word.lower(),'n')
            selectedwords.append(word+'/N')
        if tag[0] == 'V' and word.isalpha() and not is_stopword(word.lower()):
            word = wordnet_lemm.lemmatize(word.lower(),'v')
            selectedwords.append(word+'/V')

    return ' '.join(selectedwords)
   

def process_text(text):
    sents_words = []
    senlist = nltk.sent_tokenize(text)
    for sen in senli
        wordstr = process_sents(sen)
        if len(wordstr)!=0 : sents_words.append(wordstr)
    
    return ';'.join(sents_words)

stopword_list = None
def is_stopword(word):
    global stopword_list
    if stopword_list is None:
        f=open('stopwords.txt')
        s = f.readline()
        f.close()
        stopword_list = s.split(' ')
    
    return word in stopword_list

def stats_wordfreq(dbpath='../documents.db'):
    con = sqlite3.connect(dbpath)
    cur0 = con.cursor()
    cur0.execute("create table word_idf(word text primary key, idf number)")
    
    cur = con.cursor()
    cur.execute('select title, content from seg_words')
    words = {}
    for r in cur:
        temp = set()
        text = r[0] + ';' + r[1]
        for sent in text.split(';'):
            for wc in sent.split(' '):
                temp.add(wc[0:-2])

        for w in temp:
            if w not in words: words[w] = 1
            else: words[w] += 1

        if len(words) >= 10000:
            for w in words:
                cur0.execute('select idf from word_idf where word=?', (w,))
                idf_row = cur0.fetchone()
                count = words[w]
                if idf_row is None:
                    cur0.execute('insert into word_idf(word,idf) values(?,?)', (w,count))
                else:
                    cur0.execute('update word_idf set idf=? where word=?', (idf_row[0]+count, w))
            con.commit()
            words.clear()
            
    for w in words:
        cur0.execute('select idf from word_idf where word=?', (w,))
        idf_row = cur0.fetchone()
        count = words[w]
        if idf_row is None:
            cur0.execute('insert into word_idf(word,idf) values(?,?)', (w,count))
        else:
            cur0.execute('update word_idf set idf=? where word=?', (idf_row[0]+count, w))
    con.commit()
    con.close()


def add_domain_field(dbpath='../documents.db'):
    con = sqlite3.connect(dbpath)
    cur = con.cursor()
    cur2 = con.cursor()
    cur.execute("alter table seg_words add domain text")
    cur.execute("select docid, domain from document")
    for r in cur:
      cur2.execute("update seg_words set domain=? where docid=?", (r[1],r[0]) )
    con.commit()
    con.close()

if __name__ == '__main__':
    db_file=r"F:\xhe\my_code\workspace\semantic_community\documents.db"
    seg_text(db_file)
