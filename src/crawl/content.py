import codecs

"""
the parse page content
"""

import re,os,time
from bs4 import BeautifulSoup
import dwutil

def parse_content(url, title=None):
    """http://news.qq.com/a/20121120/002046.htm"""
    page = dwutil.downloadPage(url)
    if not page:
        print "failed to downlod url '%s'" % (url,)  
        return
    page = page.decode('gb18030')
    soup = BeautifulSoup(page, 'lxml')
    #remove script and style tags
    for elem in soup.findAll(['script','style']):
        elem.extract()
    if not title:
        ttag = soup.find('h1')
        if not ttag: return None
        title = ttag.text.strip()

    ctag = soup.find(id='Cnt-Main-Article-QQ')
    if ctag == None:
        print "failed to extract content from '%s'" % (url,)  
        return None
    plist = []
    ptags = ctag.find_all('p')
    #print ptags
    for p in ptags:
        p = p.text.strip()
        if p: plist.append(p)
    if not plist:
        print 'can not find paragraph in content page: %s' % url
        return None
    content = '\n'.join(plist)
    return (content, title)


def fetch_content(dbcon, save_path):
    cur = dbcon.execute('select rowid,url,title,topic,pub_time from urllist where downloaded=0')
    total,success = 0,0
    for r in cur:
        total += 1
        rid, url,title,topic,pub_time = r
        dire = os.path.join(save_path,topic)
        if not os.path.exists(dire): os.mkdir(dire)

        filename = dwutil.url2filename(url)
        filepath = os.path.join(dire,filename)
        tempfile = os.path.join(save_path,'.temp.txt')
        
        if os.path.exists(tempfile): 
            print 'warn: %s exists in Directory %s',(filename,dire)
        fp = codecs.open(tempfile, encoding='utf-8', mode='w')
        content_title = parse_content(url, title)
        if content_title:
            fp.write(content_title[1])
            fp.write(u'\n')
            fp.write(pub_time)
            fp.write(u'\n')
            fp.write(content_title[0])
            fp.close()
            os.rename(tempfile,filepath)

            dbcon.execute('update urllist set downloaded=1 where rowid='+str(rid))
            success +=1
            dbcon.commit()
        #time.sleep(0.3)
    return (total,success)

if __name__ == '__main__':
    url = "http://news.qq.com/a/20130130/000036.htm"
    content,title = parse_content(url)
    print content,title
