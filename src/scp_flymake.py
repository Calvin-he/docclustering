import igraph
import itertools,math
from operator import mul

class UnionFind:
    """Union-find data structure.

    Each unionFind instance X maintains a family of disjoint sets of
    hashable objects, supporting the following two methods:

    - X[item] returns a name for the set containing the given item.
      Each set is named by an arbitrarily-chosen one of its members; as
      long as the set remains unchanged it will keep the same name. If
      the item is not yet part of a set in X, a new singleton set is
      created for it.

    - X.union(item1, item2, ...) merges the sets containing each item
      into a single larger set.  If any item is not yet part of a set
      in X, it is added to X as one of the members of the merged set.
    """

    def __init__(self):
        """Create a new empty union-find structure."""
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        """Find and return the name of the set containing the object."""

        # check for previously unknown object
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root
        
    def __iter__(self):
        """Iterate through all items ever found or unioned by this structure."""
        return iter(self.parents)

    def union(self, objects):
        """Find the sets containing the objects and merge them all."""
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r],r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest

class Clique(object):
    """
    A class for presenting cliques of size k. Realizations
    of this class just hold a sorted list of nodes in the clique.
    """
    def __init__(self,nodelist,notSorted=True):
        self.nodes=nodelist
        if notSorted:
            self.nodes.sort()
        self.hash=None
        self.weight = None
    def __hash__(self):
        if self.hash==None:
            self.hash=hash(reduce(mul,map(self.nodes[0].__class__.__hash__,self.nodes)))
        return self.hash
    def __iter__(self):
        for node in self.nodes:
            yield node
    def __hash__(self):
        if self.hash==None:
            self.hash=hash(reduce(mul,map(self.nodes[0].__class__.__hash__,self.nodes)))
        return self.hash
    def __eq__(self,kclique):
        return self.nodes == kclique.nodes

    def __len__(self):
        return len(self.nodes)
    def getSubcliques(self):
        for i in range(0,len(self.nodes)):
            yield Clique(self.nodes[:i]+self.nodes[(i+1):],notSorted=False)
    def __str__(self):
        return str(self.nodes)
    # def getEdges(self):
    #     for node in self.nodes:
    #         for othernode in selfnodes:
    #             if node!=othernode:
    #                yield (node,othernode)
    def getWeight(self, graph):
        if self.weight == None:
            self.weight=self.intensity(graph)
        return self.weight

    def intensity(self, graph):
        intens = 1
        for edge in itertools.combinations(self.nodes,2):
            intens *= graph[edge]
        return math.pow(intens, 1.0/len(self.nodes))

    

def findKCliques(graph, k, source, target):
    if k==2:
        yield Clique([source,target])
    else:
        s_deg, t_deg = graph.degree(source), graph.degree(target)
        if(s_deg > t_deg):  #make sure of source's degree not larger than target's
            temp=source; source=target; target=temp
        if s_deg>k-3 and t_deg>k-3:
            if k==3:
                for nv in graph.neighbors(source):
                    if graph[nv,target]>0:
                        yield Clique([source, target, nv])
            elif k==4:
                commonVertices = [nv for nv in graph.neighbors(source) if graph[nv,target]>0]
                for npair in itertools.combinations(commonVertices,2):
                    if graph[npair]>0:
                        yield Clique([source,target,npair[0],npair[1]])
            else:
                commonVertices = [nv for nv in graph.neighbors(source) if graph[nv,target]>0]
                for vs in itertools.combinations(commonVertices,k-2):
                    for vp in itertools.combinations(vs,2):
                        if graph[vp]==0: break
                    yield Clique([source,target]+list(vs))
    graph.add_edge(source,target)

                        
def findkCommunities(cliquelist):
    ctree = UnionFind()
    while len(cliquelist)!=0:
        c = cliquelist.pop()
        ctree.union(list(c.getSubcliques()))
    
    group = {}
    for clique in ctree:
        root = ctree[clique]
        if root not in group:
            group[root] = set(iter(clique))
        else:
            group[root].update(set(iter(clique)))
        
    return group.itervalues()


def communities_scp(graph,k):
    subgraph=igraph.Graph(n=graph.vcount(), directed=False)
    cliquelist = []
    print 'finding %d-cliques...' % (k,)
    for e in graph.es:
        for clique in findKCliques(subgraph, k, e.source, e.target):
            cliquelist.append(clique)

    del subgraph
    print 'count of cliques: '+str(len(cliquelist))
    #sort in ascending order
    cliquelist.sort(cmp=lambda lc,rc:1 if (lc.getWeight(graph) > rc.getWeight(graph)) else 0)
    
    print 'finding %d-communities...' % (k,)
    return igraph.VertexCover(graph, findkCommunities(cliquelist))

 # ef communities_scp(UG, k):
 #    ''' SCP community detection algorithm
 #    '''
 #    cnet = igraphToNet(UG)
    
 #    kcw = kcliquesWeight(cnet, k, weightFunction=kc.getIntensity)
 #    kcliques = kc.EvaluatiocommonVertices(kcw, weightFunction=lambda x:kc.getIntensity(x,net))
 #    kcliques.setLastEvaluation()
 #    node_fam = list(kc.communitiesByKCliques(kcliques))[0]
    
 #    VertexCover = igraph.VertexCover(UG, )
    
        

# def igraphToNet(UG):
#     '''convert  Graph Type of igraph into kclique's SymmNet
#     '''
#     assert not UG.directed()
#     newNet = kclique.SymmNet()
#     for e in UG.es:
#         newNet[e.tuple] = e['weight']
#     return newNet
