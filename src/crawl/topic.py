import sqlite3
import sys,os
import urllist,content
import argparse
import codecs

def createdb(dbname='urllist.sqlite'):
    con = sqlite3.connect(dbname)
    con.execute("""create table if not exists urllist(url text unique not null,
title text not null,
pub_time text not null,
topic text not null,
downloaded integer default 0)""")
    return con

def download_urllist(args):
    con = createdb(args.urldb)
    f = codecs.open(args.urllist,'r','utf-8')
    for topic in f:
        if topic[0] == '#': continue
        s = topic.split()
        topicurl,topicname = s[0],s[1]
        print 'processing '+topic
        save_urllist(con, topicurl, topicname, args.maxpage)
    con.commit()
    con.close()

def save_urllist(dbcon, topicUrl, topicname, maxpagenum):
    ulist = urllist.get_urllist(topicUrl, topicname, maxpagenum)
    for link,title,pubtime,tname in ulist:
        try:
            dbcon.execute("INSERT INTO urllist(title, url,pub_time,topic) VALUES(?,?,?,?)", (title,link,pubtime,tname))
        except:
            pass
    dbcon.commit()

def download_content(args):
    con =  sqlite3.connect(args.urldb)
    if not os.path.exists(args.content):
        os.makedirs(args.content)
    
    total, suc = content.fetch_content(con,args.content)
    print "success=%d/total=%d" % (suc,total)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--urldb', help='where to save the url db file?', required=True)
    parser.add_argument('-u', '--urllist', help="download urllist from the topic file")
    parser.add_argument('-c', '--content', help="save the content of url")
    parser.add_argument('-n', '--maxpage', type=int, help="max page number to navigate for a topic", default=100)
    args = parser.parse_args()

    if args.urllist:
        print "downloading url list..."
        download_urllist(args)
        print "complete url list downloading."

    if args.content:
        print 'downloading content...'
        download_content(args)
        print 'complete content downloading.'

if __name__ == '__main__':
    main()
