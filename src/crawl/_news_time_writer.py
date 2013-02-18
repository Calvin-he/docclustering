import argparse
import sqlite3
import os,codecs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--urldb', help='where is the url db file?', required=True)
    parser.add_argument('-d', '--newsdir', help="where is the root directory of news topic", required=True)
    argv = parser.parse_args()

    con = sqlite3.connect(argv.urldb)
    for r in con.execute('select url, topic, pub_time from urllist'):
        filename = r[0][r[0].rindex('/')+1:]
        filepath = os.path.join(argv.newsdir, r[1], filename)
        if os.path.exists(filepath):
            data = codecs.open(filepath,'r','gb18030',errors='ignore').readlines()
            data[1] = r[2]
            out = codecs.open(filepath,'w','utf-8')
            out.writelines(data)
            out.close()
    con.close()

if __name__ == '__main__':
    main()









