# -*- encoding=utf-8 -*-
import dwutil
import bs4,os,re,codecs

def get_urllist(curl):
    page = dwutil.downloadPage(curl)
    page = page.decode('gb18030','ignore')   
    urlmatcher = re.compile(r'^http://(\w+\.)+qq\.com/\w+/\d+/\d+\.htm$')
    soup = bs4.BeautifulSoup(page)
    alist = soup.find_all('a', href=urlmatcher)
    
    if len(alist) == 0:
        print 'failed to find urllist from %s' % (curl,)
    else:
        for a in alist:
            link,title = a['href'], a.text.strip()
            yield (link, title)
            
def parse_link(url, title=None):
    """http://news.qq.com/a/20121120/002046.htm"""
    page = dwutil.downloadPage(url)
    if not page:
        print "failed to downlod url '%s'" % (url,)  
        return None
    page = page.decode('gb18030','ignore')
    soup = bs4.BeautifulSoup(page, 'lxml')
    #remove script and style tags
    for elem in soup.findAll(['script','style']):
        elem.extract()
    if not title:
        ttag = soup.find('h1')
        if not ttag: return None
        title = ttag.text.strip()
    pub_time = soup.find('span', class_=re.compile('pubTime|article-time'))
    if not pub_time:
        print 'warn: %s has no pubtime' % url
        return None
    pub_time = pub_time.text
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
    return (content, title,pub_time)


def download_noise(url = 'http://www.qq.com'):
    rootdir = '../../data/noise'
    #os.makedirs(rootdir)

    for link, title in get_urllist(url):
        idx = link.index('/',8)+1
        fname = link[idx:].replace('/','')  
        fname = os.path.join(rootdir,fname)
        
        if os.path.exists(fname): continue
        ct_tt_tm = parse_link(link,title)
        if ct_tt_tm == None: continue
        f = codecs.open(fname, 'w', 'utf-8')
        f.write(ct_tt_tm[1])
        f.write(u'\n')
        f.write(ct_tt_tm[2])
        f.write(u'\n')
        f.write(ct_tt_tm[0])
        f.close()
    
def mix_dir(destdir, num=60):
    import random, shutil
    rootdir = '/home/cs/src/semantic_community/data/noise'
    files = os.listdir(rootdir)
    samp = random.sample(xrange(len(files)),num)
    r = xrange(len(files))
    for fi in samp:
        dst =os.path.join(destdir, 'noise_'+str(fi)) 
        os.mkdir(dst)
        shutil.copy(os.path.join(rootdir,files[fi]), dst) 

if __name__ == '__main__':
    # download_noise('http://www.qq.com/')
    # download_noise('http://news.qq.com/')
    # download_noise('http://ent.qq.com/')
    # download_noise('http://lady.qq.com/')
    # download_noise('http://comic.qq.com/')
    # download_noise('http://astro.lady.qq.com/')
    # download_noise('http://finance.qq.com/')
    # download_noise('http://auto.qq.com/')
    # download_noise('http://house.qq.com/')
    # download_noise('http://tech.qq.com/')
    # download_noise('http://digi.tech.qq.com/')
    # download_noise('http://games.qq.com/')
    # download_noise('http://edu.qq.com/')
    # download_noise('http://book.qq.com/')
    # download_noise('http://baby.qq.com/')
    # download_noise('http://gongyi.qq.com/')
    download_noise('http://news.qq.com/paihangz.htm')
    download_noise('http://news.qq.com/paihang.htm')











