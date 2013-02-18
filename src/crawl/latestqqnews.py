import urllib2
import random

def fetchlist(numofpage=1, cata='newsgn'):
    base = 'http://roll.news.qq.com/'
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    r = opener.urlopen(base)

    for n in range(1,numofpage+1):
        url = '/interface/roll.php?%f&cata=%s&site=news&date=&page=%d&mode=1&of=json' % (random.random(),cata,n)
        r = conn.urlopen(url)
        yield r.data
    conn.close()

