# encoding=utf8

import dwutil
import bs4

def get_topiclist(url):
    """http://news.qq.com/topic/gnzt.htm """
    page = dwutil.downloadPage(url)
    page = page.decode('gb18030')

    soup = bs4.BeautifulSoup(page,'lxml')
    alist = soup.find_all('a', class_='black linkcss fsize14')
    for a in alist:
        u =  a['href']
        i = u.index('zt/')
        u = u[:i+2]+u[i+3:]
        p = dwutil.downloadPage(u)
        p = p.decode('gb18030')
        soup2 = bs4.BeautifulSoup(p,'lxml')
        
        turl = soup2.find('a', text=u'最新消息')
        if turl == None: continue
        link = turl['href']
        
        date = a.next_sibling.text
        # remove the '(' and ')' in (2013年02月01日)
        date = date[1:-1]
        tname = a.text
        yield (link,tname,date)
    
def main():
    import sys
    url = sys.argv[1]
    outfile =sys.argv[2]
    f = open(outfile, 'w')
    for x in get_topiclist(url):
        line = '\t'.join(x).encode('utf8')
        f.write(line)
        f.write('\r\n')
    f.close()

if __name__ == '__main__':
    main()





