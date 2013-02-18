import igraph
import dbutils
import xhe_utils as utils

def loadTitleWordnet(dbfile='../data/cn-topic.db', min_coocur=2, min_weight=1e-3):
    dbcon = dbutils.connect_db(dbfile)
   
    #g = igraph.Graph(directed=False)
    #g.vs['name']=None
    #edge_size =dbutils.countOfRecs(dbcon,'t_wordpair','coocur_num>=? and weight>?', (min_coocur,min_weight))
    #cnt = 0;
    edgelist = []
    for r in dbutils.iterRec(dbcon,'t_wordpair',['word1', 'word2','weight'], 'coocur_num>=? and weight>?', (min_coocur,min_weight)):
        edgelist.append({'source':r[0], 'target':r[1], 'weight':r[2]})
        #cnt+=1
        #if cnt%100==0:
        #    utils.updateProgress(cnt, edge_size)
    #print ''
    dbutils.close_db(dbcon)
    return igraph.Graph.DictList(vertices=None, edges=edgelist)
