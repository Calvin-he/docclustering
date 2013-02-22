import os,re,codecs
import anydbm
from pyictclas import PyICTCLAS, CodeType, POSMap

class WordDF:
    def __init__(self, mode='r', datadir='../data'):
        """ mode is r(read) or w(write) """
        self._worddbpath = os.path.join(datadir,'worddf.adb')
        self._filedbpath = os.path.join(datadir,'worddf_file.adb')
        if mode == 'r':
            self.ictclas = None
        elif mode == 'w':
            self.ictclas = self.__load_ictclas()
        elif mode == 'c':
            if os.path.exists(self._worddbpath):
                os.remove(self._worddbpath)
            if os.path.exists(self._filedbpath):
                os.remove(self._filedbpath)
            self.ictclas = self.__load_ictclas()
        self.worddb = anydbm.open(self._worddbpath, mode)
        self.filedb = anydbm.open(self._filedbpath, mode)

    def add_docs(self, rootdir, encoding='utf-8'):
        fnm = re.compile(r'\.htm$|\.txt$') 
        for root,dirs,files in os.walk(rootdir):
            print 'scanning dir: ', root
            for f in files:
                if f.endswith('.htm') or f.endswith('.txt'):
                    fp = os.path.join(root,f)
                    if not self.__is_processed(f):
                        words = self.__stats_word(fp, encoding)
                        if len(words)>10:
                            self.__add_words(words, f)

    def add_docs_from_db(self,db):
        if isinstance(db,basestring):
            import sqlite3
            dbcon = sqlite3.connect(db)

        for r in dbcon.execute('select docid,title, content from document'):
            wordset = set()
            if r[1]:
                for w in r[1].split():
                    wordset.add(w)
            for w in r[2].split():
                wordset.add(w.split('/')[0])
            self.__add_words(wordset, str(r[0]))

        if isinstance(db,basestring): dbcon.close()

    def df(self, word):
        if type(word) == unicode:
            word = word.encode('utf-8')
        try:
            return int(self.worddb[word])
        except KeyError:
            return 0

    def doc_size(self):
        return len(self.filedb)

    def close(self):
        if self.worddb:
            self.worddb.close()
        if self.filedb:
            self.filedb.close()
        if self.ictclas:
            self.ictclas.ictclas_exit()

    def __load_ictclas(self):
        ict = PyICTCLAS('/home/cs/src/semantic_community/lib/ICTCLAS/libICTCLAS50.so')
        if not ict.ictclas_init('/home/cs/src/semantic_community/lib/ICTCLAS'):
            print 'faied to initial ictclas'
            exit()
        if not ict.ictclas_importUserDict('/home/cs/src/semantic_community/lib/ICTCLAS/userdict.txt', CodeType.CODE_TYPE_GB):
            print 'failed to inital importing user dict to ictclas'
            exit()
        ict.ictclas_setPOSmap(POSMap.PKU_POS_MAP_FIRST)
        self.ictclas = ict
        return self.ictclas
    
  
    def __is_processed(self, fp):
        return self.filedb.has_key(fp)

    def __stats_word(self, filepath, encoding):
        if self.ictclas == None:
            self.__load_ictclas()
        text = u''
        try:
            f = codecs.open(filepath,'r',encoding, errors='strict')
            text = f.read()
            f.close()
        except:
            f.close()
        if len(text)<20: return set()
        text = text.encode('gb18030')
        res = self.ictclas.ictclas_paragraphProcess(text, CodeType.CODE_TYPE_GB)
        words = res.value.decode('gb18030','ignore')
        wordset = set()
        for wt in words.split():
            i = wt.find('/')
            if i<0:
                print 'unexpected word tag', wt
            word,tag = wt[:i],wt[i+1:]
            if (tag == 'n' or tag == 'v') and len(word)>=2:
                wordset.add(word)
        return wordset

    def __add_words(self,words,filepath):
        for w in words:
            w = w.encode('utf-8')
            v = self.worddb.get(w)
            if v:
                self.worddb[w] = str(int(v)+1)
            else:
                self.worddb[w] = '1'
        
        self.filedb[filepath] = '1'

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--resdir', help='which to store th result df', required=True)
    p.add_argument('-c','--filecoding', help='the file encoding', default='utf-8')
    p.add_argument('indexdir', help='which dir to index words')

    args =p.parse_args()

    wdf = WordDF('w', args.resdir)
    wdf.add_docs(args.indexdir, args.filecoding)
    wdf.close()
