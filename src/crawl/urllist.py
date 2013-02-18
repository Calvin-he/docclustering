# -*- coding: gbk -*-

"""
the url list are extrated from the topic page
"""

import re
from bs4 import BeautifulSoup
import dwutil

def get_urllist(topicUrl, topicname=None, maxnumofpage=0):
    """
    http://news.qq.com/l/13532840273/list_13532840273.htm
    """
    curl = topicUrl
    urlmatcher = re.compile(r'^http://news\.qq\.com/\w+/\d+/\d+\.htm$')
    nexturlmatcher = re.compile(u'^下一页')
    numofpage = 0
    while curl != None:
        page = dwutil.downloadPage(curl)
        if page == None: break
        page = page.decode('gb18030')
        soup = BeautifulSoup(page)

        if not topicname:
            topicname = soup.find('title').text.strip()
            si = topicname.find('_')+1
            ei = topicname.find('_', si)
            topicname = topicname[si:ei]

        alist = soup.find_all('a',href=urlmatcher)
        if len(alist) == 0:
            print 'failed to find urllist from %s' % (curl,)
        else:
            for a in alist:
                link,title = a['href'], a.text.strip()
                pubtime = a.find_next_sibling('span')
                if pubtime:
                    pubtime = pubtime.text.strip()
                    yield (link, title, pubtime, topicname)
        
        numofpage += 1
        if maxnumofpage>0 and numofpage>maxnumofpage: break
        #find next page url
        anext = soup.find('a', text=nexturlmatcher) #next page
        curl = anext['href'] if anext!=None else None
    
    print "navigated %d list pages" % numofpage
 


if __name__ == '__main__':
    url = "http://news.qq.com/l/13534669977/list_13534669977.htm"
    for link,title,topicname in get_urllist(url):
        print link +','+ title +','+topicname 
    
