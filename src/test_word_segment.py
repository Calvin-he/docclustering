
import codecs
def main():
    datafile = 'word_segment_test.htm'
    f = codecs.open(datafile,'r','utf-8')
    data = f.readlines()
    print 'title:', data[0]
    print 'pubtime:', data[1]
    print 'content: ', ''.join(data[2:])
 


main()
