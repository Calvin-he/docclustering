import sqlite3
import os,codecs
from pyictclas import PyICTCLAS, CodeType, POSMap

def init_db(db_path):
    print 'initizing database...'
    db_conn = sqlite3.connect(db_path)
    db_conn.executescript('''create table if not exists document(
 docid integer primary key, 
 title text not null,
 content text not null,
 kw_title text,
 kw_content text,
 cats text not null,
 pub_time text not null);
''')
    return db_conn

stopword_set = None
def load_stopword(stopwordfile='../data/stopword_cn', encoding='utf-8'):
    """ load stop word for word segmentation """
    global stopword_set
    if not stopword_set:
        f=codecs.open(stopwordfile,'r',encoding)
        s = f.read()
        f.close()
        stopword_set = frozenset(s.split())
    return stopword_set

def load_topiclist(dbpath, rootdir):
    dbcon = init_db(dbpath)
    topics = os.listdir(rootdir)
    for tp in topics:
        tp = tp.decode('utf8')
        print 'processing topic: %s' % tp
        files = [os.path.join(rootdir,tp,f) for f  in  os.listdir(os.path.join(rootdir,tp))]
        prepro_topic(dbcon, tp, files)
    dbcon.close()

def prepro_topic(db, tp, files):
    db_con = db
    if isinstance(db,basestring):
        db_con = init_db(db)

    ict = load_ictclas()
    cnt = 0
    for filepath in files:
        fp = codecs.open(filepath,'r','utf-8')
        data = fp.readlines()
        fp.close()
        title = seg_text(ict, data[0])
        pubtime = data[1]
        content = seg_text(ict, ''.join(data[2:]))
             
        if title and content:
            db_con.execute('insert into document(title,content,cats,pub_time) values(?,?,?,?)', (title, content, tp, pubtime))
            cnt += 1

    db_con.commit()
    if isinstance(db,basestring): db_con.close()
    ict.ictclas_exit()
    return cnt

def load_ictclas():
    ict = PyICTCLAS('../lib/ICTCLAS/libICTCLAS50.so')
    if not ict.ictclas_init('../lib/ICTCLAS'):
        print 'faied to initial ictclas'
        exit()
    if not ict.ictclas_importUserDict('../lib/ICTCLAS/userdict.txt', CodeType.CODE_TYPE_GB):
        print 'failed to inital importing user dict to ictclas'
        exit()
    ict.ictclas_setPOSmap(POSMap.PKU_POS_MAP_FIRST)
    return ict


def seg_text(ictclas,text):
    #print text
    stopwords = load_stopword()
    text = text.encode('gb18030')
    res = ictclas.ictclas_paragraphProcess(text, CodeType.CODE_TYPE_GB)
    res = res.value.decode('gb18030', 'ignore')
    wordlist = ''
    for term in res.split():
        ss = term.split('/')
        if len(ss) != 2: continue
        word,pos = ss
        if len(word)<2 or word in stopwords:
            continue
        if pos == 'n' or pos == 'v':
            wordlist += ' ' + word+'/'+pos

    return wordlist
            
if __name__ == '__main__':
    import argparse
    parser =argparse.ArgumentParser()
    parser.add_argument('-f', '--dbfile', help='where to save the dbfile?', required=True)
    parser.add_argument('docdir', help='where is the root directory of documents')
    argv = parser.parse_args()
    dbpath = argv.dbfile 
    rootdir = argv.docdir

    load_topiclist(dbpath, rootdir)
    

