import nltk
from nltk import snowball
import sqlite3
import os, sys,re

stopword_set = None

def load_filelist(cats_file, db_path):
    f = open(cats_file, 'r')
    lines = f.readlines()
    f.close()
    file_num = len(lines)

    dirname = os.path.dirname(cats_file)

    load_stopword()
    db_conn = init_db(db_path)
    cnt = 0
    for line in lines:
        ss = line.split()
        file_path = dirname+u'/'+ss[0]
        cat_tag = ' '.join(ss[1:])
        (title, content) = process_doc(file_path, cat_tag)
        if len(title)==0 or len(content)==0:
            print "File '%s' is alnormal" % (ss[0],)
            continue
        save_doc(db_conn, title, content, cat_tag, file_path)
        
        cnt += 1
        if cnt%10 == 0:
            perc = '{0:.0%}'.format(float(cnt)/file_num)
            sys.stdout.write('\rfinished=%d/total=%d, %s finished' %(cnt, file_num, perc))
            sys.stdout.flush()
    print ''
    close_db(db_conn)


def load_stopword():
    global stopword_set
    if stopword_set is None:
        f=open('../data/stopwords', 'r')
        s = f.read()
        f.close()
        stopword_set = frozenset(s.split())

def init_db(db_path):
    print 'initizing database...'
    db_conn = sqlite3.connect(db_path)
    db_conn.executescript('''create table document (
 docid integer primary key, 
 title text not null,
 content text not null,
 kw_title text,
 kw_content text,
 cats text not null,
 file_path text not null);

create table sdocument (
 docid integer primary key, 
 title text not null,
 content text not null,
 kw_title text,
 kw_content text,
 cats text not null,
 file_path text not null);

 create table cate (name text,
 docid integer not null)
''')
    return db_conn


def save_doc(db_conn, title, content, cat_tag, file_path):
    title_str = ' '.join( [ '/'.join(w) for w in title] )
    content_str = ' '.join( [ '/'.join(w) for w in content] )
    # for sent in content:
    #     content_str += ' '.join( [ '/'.join(w) for w in sent ] ) + '\n'
    # content_str = content_str[0:-1] #remove the last char '\n'
    #print content_str
    #print cat_tag
    cur = db_conn.cursor()
    cur = db_conn.execute('''insert into document(title, content, cats,file_path ) 
values (?,?,?,?)''', (title_str, content_str, cat_tag, file_path))
    docid = cur.lastrowid 
    cat_did = map(lambda e:(e,docid), cat_tag.split())
    cur.executemany('''insert into cate(name, docid) values(?,?)''', cat_did)
    cur.close()                 
    

def close_db(db_conn):
    db_conn.commit()
    db_conn.close()

def process_doc(news_file, cat_set):
    title, content = load_doc(news_file)
    #print 'Title: %s \n Content: %s' % (title, content)
    title, content = segment_word(title, content)
    return (title,content)

def load_doc(news_file):
    f = open(news_file)
    title = f.readline()
    content = f.read()
    f.close()
    return (title, content)

def pos_text(text):
    tokens = nltk.word_tokenize(text)     
    wordtags = nltk.pos_tag(tokens)
    
    stemmer = nltk.PorterStemmer()
    selectedwords = []
    patn = re.compile('[^a-zA-Z\-]')
    for (word,tag) in wordtags:
        word = patn.sub('', word)
        lword = word.lower()
        if lword in stopword_set or len(word)<=1: continue
        if tag[0] == 'N':         
            nword = stemmer.stem_word(lword)
            selectedwords.append((nword, word, 'N'))
        elif tag[0] == 'V':
            nword = stemmer.stem_word(lword)
            selectedwords.append((nword, word, 'V'))
        elif tag[0] == 'J':
            nword = stemmer.stem_word(lword)
            selectedwords.append((nword, word, 'J'))
        # elif tag[0] == 'R':
        #     word = nltk.WordNetLemmatizer().lemmatize(word,'r')
        #     selectedwords.append(word+'/R')
        # if word not in stopword_set:
        #     word = nltk.WordNetLemmatizer().lemmatize(word)
        #     selectedwords.append(word)

    return selectedwords


def segment_word(title, content):
    title_words = pos_text(title)
    content_words = pos_text(content)
    # sentlist = nltk.sent_tokenize(content)
    # for s in sentlist:
    #     words = pos_text(s)
    #     if len(words): 
    #         content_words.append(words)
    return (title_words, content_words)

def test():
    load_stopword()
    conn = init_db('test.db')
    (t,c) = process_doc('~/nltk_data/corpora/reuters/test/148440', 'test')
    save_doc(conn, t, c, 'test', 'ignore')
    close_db(conn)
    
def select_expr_data(db_con):
    """select expriment data from origal data set"""
    sql = """INSERT INTO document(docid,title,content,cats,file_path)
SELECT docid, title, content, cats, file_path  from org_document WHERE docid IN
(SELECT distinct(docid) FROM cate WHERE cate.name 
  IN (SELECT name FROM cate GROUP BY  name  HAVING count(docid)>=90))"""
    cur = db_con.execute(sql)


def main():
    cat_file = '/home/cs/src/semantic_community/dataset/reuters-21578/cats.txt'
    db_path = './reuters2.db'
    
    
    load_filelist(cat_file,db_path)


if __name__=='__main__':
    main()
