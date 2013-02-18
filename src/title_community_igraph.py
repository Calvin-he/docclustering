import sqlite3
from igraph import *
import extract_keyword as ek

def read_graph(db_path='reuters2.db', min_coocur=3, min_weight=1e-2, directed=False):
    db_conn = sqlite3.connect(db_path)
    
    G = Graph()
    id_word_dict = {}
    if not directed:
        sql = 'select wid1, wid2, weight from title_coword where coocur_num>=?'
        cur = db_conn.execute(sql, (min_coocur,))        
        id_pair_list = cur.fetchall()

        for wid1, wid2, _ in id_pair_list:
            get_word_by_id(db_conn, id_word_dict, wid1)
            get_word_by_id(db_conn, id_word_dict, wid2)
        
        G.add_vertices(id_word_dict.itervalues())
        for wid1, wid2, w in id_pair_list:
            word1 = get_word_by_id(db_conn, id_word_dict, wid1)
            word2 = get_word_by_id(db_conn, id_word_dict, wid2)
            G.add_edge(word1, word2, weight=w)
    else:
        raise Exception('not implement yet')
    db_conn.close()
    return G

def get_word_by_id(db_conn, id_word_dict, wid):
    if wid not in id_word_dict:
        id_word_dict[wid] = ek.get_org_words_by_id(db_conn, wid)
    return id_word_dict[wid]
