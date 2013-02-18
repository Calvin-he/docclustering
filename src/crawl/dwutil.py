import urllib2

def downloadPage(url):
    try:
        urlstream = urllib2.urlopen(url)
        htmsrc = urlstream.read()
        urlstream.close()
        return htmsrc
    except Exception:
        print 'failed to download page from %s' % (url,)
        return None

def url2filename(url):
    """
    http://news.qq.com/a/20130217/000046.htm
    """
    s = url.rindex('/', 0, url.rindex('/'))+1
    return url[s:].replace('/','')
