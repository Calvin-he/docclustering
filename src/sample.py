# -*- encoding=utf-8 -*-
"""
抽取样本作性能测试实验
"""
import os
from CommunityBuilder import CommunityBuilder

def sample_docs(num=500, srcdir='../data/newsgn'):
    sfiles = []

    i=0
    for root, dirs, files in os.walk(srcdir):
        for f in files:
            if not f.endswith('.htm'): continue
            fp = os.path.join(root,f)
            if i<num:
                sfiles.append(fp)
                i += 1
    # if not os.path.exists(distdir):
    #     os.makedirs(distdir)
    
    #for f in sfiles:
    #    shutil.copy(f, distdir)
    return sfiles

def main():
    import preproc_qqtopic
    import extract_keyword
    import worddf
    dbfile = '../data/time_test.db'
    logtimefile = '../result/time_test.log'
    
    timefile = open(logtimefile,'w')
    timefile.write('ndocs\ttime(sec)\n')
    rang = xrange(500,7500, 500)
    for num in rang:
        files = sample_docs(num,'../data/newsgn')
        if os.path.exists(dbfile):
            os.remove(dbfile)
        
        preproc_qqtopic.prepro_topic(dbfile,'time_test', files)
  
        wdf = worddf.WordDF('c')
        wdf.add_docs_from_db(dbfile)
        wdf.close()

        dbcon = extract_keyword.init_db(dbfile)
        extract_keyword.word_preproc(dbcon)
        extract_keyword.title_keyword(dbcon)
        extract_keyword.title_df(dbcon)
        extract_keyword.content_keyword(dbcon)
        extract_keyword.topic_keyword(dbcon)
        dbcon.close()
   

        cb = CommunityBuilder(dbfile)
        time,c = 0.0,6
        print 'time_test %d' % num
        for i in range(c):
            cb.build()
            time += cb._run_time
        timefile.write('%d\t%.3f\n' % (num, time/c))

    timefile.close()

if __name__ == '__main__':
    main()
