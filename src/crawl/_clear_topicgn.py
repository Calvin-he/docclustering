import codecs
import os

def main():
    rootdir = '../../data/topicgn/'
    for dirpath, dnames, fnames in os.walk(rootdir):
        for f in  fnames:
            print f
            path = os.path.join(dirpath,f)
            f = open(path, 'r')
            reserve = []
            for line in  f.readlines():
                line = line.strip('\t')
                if line and not line.startswith('.Video') and not line.startswith('.video') and not line.startswith('flash_') and not line.startswith('var ') and not line.startswith('background:'):
                    reserve.append(line)
            f.close()

            f = open(path,'w')
            f.writelines(reserve)
            f.close()



main()





