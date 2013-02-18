import sqlite3
import networkx as nx
import community
import matplotlib.pyplot as plt
import pylab 

def read_graph(db_path, min_coocur=3, min_weight=1e-2, directed=False):
    db_conn = sqlite3.connect(db_path)
    graph_name = 'Title associated words graph'
    if directed:
        G = nx.DiGraph(name=graph_name)
        cur=db_conn.execute('select wid1, wid2, weight relation from title_coword where coocur_num>=? and weight>=?', (min_coocur, min_weight))
        G.add_weighted_edges_from(cur.fetchall())
        cur= db_conn.execute('select wid2, wid1, rweight relation from title_coword where coocur_num>=? and rweight>=?', (min_coocur, min_weight))
        G.add_weighted_edges_from(cur.fetchall())
        db_conn.close()
        return G
    else:
        G = nx.Graph(name=graph_name)
        sql = 'select wid1, wid2, max(weight, rweight) as relation from title_coword where coocur_num>=? and relation>=?'
        cur = db_conn.execute(sql, (min_coocur, min_weight))
        G.add_weighted_edges_from(cur.fetchall())
        db_conn.close()
        return G

def write_graph(G, save_path):
    print "writing graph into file '%s'" % save_path
    nx.write_weighted_edgelist(G, save_path)

def get_node_label(db_path, nodelist):
    import extract_keyword as ek
    id_word_dict = dict()
    db_conn = sqlite3.connect(db_path)
    for node in nodelist:
        word = ek.get_org_words_by_id(db_conn, node)
        id_word_dict[node] = word
    db_conn.close()
    return id_word_dict

# for r in cur:
#     G.add_edge(r[0], r[1], weight = r[2])
# db_conn.close()

db_path = '/home/cs/src/expriment/reuters2.db'
G = read_graph(db_path)

id_word_dict = get_node_label(db_path, G.nodes())
nx.relabel_nodes(G, id_word_dict)


partition = community.best_partition(G)
#drawing
size = len(set(partition.values()))
print 'generate num of communities: %d' % size

cnt = 0
nodes_list = [[] for i in range(0,size)]
for node,com_id in partition.iteritems():
    nodes_list[com_id].append(node)
nodes_list.sort(key=lambda x:len(x), reverse=True)

# plt.plot(range(1, size+1), [len(com) for com in nodes_list])
# plt.show()

pos = nx.spring_layout(G)
nodes_list = [com for com in nodes_list if len(com)>100]
cnt = 0
size = len(nodes_list)

#for com in nodes_list:
#    for  nx.clustering(com)

#node_labeles = get_node_label(db_path, G.nodes())
cm = pylab.get_cmap('gist_rainbow')
for com in nodes_list:
    color = cm(1.*cnt/size)
    nx.draw_networkx_nodes(G, pos, com, node_size=50, 
                           node_color=color)
    #nx.draw_networkx_labels(G,pos, com[0:3]
    nx.draw_networkx_edges(G, pos, G.edges(com), alpha=0.3)
    cnt += 1
#nx.draw_networkx_labels(G,pos)

pylab.show()
