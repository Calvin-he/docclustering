from igraph import Graph

class CommunityDetection:
    def __init__(self, min_nodes=10):
        self.min_nodes = min_nodes

    def detect(self, graph):
        raise NotImplementedError

    def comids_to_names(self, graph, coms):
        com_names = []
        for com in coms:
            nameset = frozenset(graph.vs.select(com)['names'])
            com_names.append(nameset)
        return com_names

class SCPCommunityDetection(CommunityDetection):
    def __init__(self, k=3, min_nodes=12):
        CommunityDetection.__init__(self, min_nodes)
        self.k=k

    def detect(self,graph):
        import scp
        return scp.communities_scp(graph,self.k, self.min_nodes)



class MulLevelCommunityDetection(CommunityDetection):
 
    def detect(self,graph):
        vc = graph.community_multilevel(weights='weight')
        coms = [c for c in vc if len(c)>=self.min_nodes]
        return coms



class LabelCommunityDetection(CommunityDetection):
    def detect(self,graph):
        vc = graph.community_label_propagation(weights='weight')
        coms = [c for c in vc if len(c)>=self.min_nodes]
        return coms


class WalkCommunityDetection(CommunityDetection):
    def detect(self,graph):
        h = graph.community_walktrap(weights='weight')
        vc = h.as_clustering()
        coms = [c for c in vc if len(c)>=self.min_nodes]
        return coms

class GreedyCommunityDetection(CommunityDetection):
    def detect(self, graph):
        h = graph.community_fastgreedy(weights='weight')
        vc = h.as_clustering()
        coms = [c for c in vc if len(c)>=self.min_nodes]
        return coms

class InfomapCommunityDetection(CommunityDetection):
    def detect(self,graph):
        vc = graph.community_infomap(edge_weights='weight')
        coms = [c for c in vc if len(c)>=self.min_nodes]
        return coms





