from igraph import *
import scp

def drawCommunities(graph,communities):
    nodes = set()
    colors = ClusterColoringPalette(len(communities))
    i =0
    fig = Plot()
    for com in communities:
        sg = graph.subgraph(com)
        for v in graph.vs: v['color'] = colors[i]
        i += 1
        fig.add(sg)

    fig.show()
    


def write_communities_scp(graph, filename):
    comus = scp.communities_scp(graph,3,10)
    comu_names = scp.comuid2name(graph, comus)
    f = open(filename)
    for com in comu_names:
        s = ' '.join(com) + '\r\n'
        f.write(s.encode('gb18030'))
    f.close()
    
def get_vertexcover_scp(graph):
    comus = scp.communities_scp(graph,3,10)
    comu_names = scp.comuid2name(graph, comus)
    nameset = set()
    for names in comu_names:
        nameset.update(names)
    sg = graph.subgraph(nameset)
    comu_ids = scp.comuname2id(sg,comu_names)
    cover = VertexCover(sg,comu_ids)

    return cover
