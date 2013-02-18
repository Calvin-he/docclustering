import itertools,math
from operator import mul
 
class KCliqueTree:
    def __init__(self, trackNodeGroup=True):
        self.weights = {}
        self.parents = {}
 
        self.trackNodeGroup = trackNodeGroup
        if self.trackNodeGroup:
            self.node_groups = {}
            self.largest = 0
            self.seclargest = 0
          
    def __getitem__(self, cliq):
        """Find and return the name of the set containing the cliq."""
        # check for previously unknown cliq
        if cliq not in self.parents:
            self.parents[cliq] = cliq
            self.weights[cliq] = 1
            if self.trackNodeGroup:
                self.node_groups[cliq]=set(cliq)
            return cliq

        # find path of objects leading to the root
        path = [cliq]
        root = self.parents[cliq]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def sumOfGroupSize(self):
        if self.trackNodeGroup:
            val = 0
            for v in self.node_groups.itervalues():
                val += len(v)
            return val
        else: raise NotImplemented

    def numOfGroup(self):
        return len(self.node_groups)

    def hasClique(self,clique):
        return self.parents.has_key(clique)

    def union(self, objects):
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r],r) for r in roots])[1]
        for r in roots:
            if r != heaviest and self.parents[r] != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest
                if self.trackNodeGroup:
                    self.node_groups[heaviest].update(self.node_groups[r])
                    del self.node_groups[r]

        if self.trackNodeGroup:
            size = len(self.node_groups[heaviest])
            if size > self.seclargest:
                if size > self.largest:
                    self.seclargest = self.largest
                    self.largest = size
                else:
                    self.seclargest = size
        #return the root
        return heaviest
    
    def getNodegroups(self):
        if self.trackNodeGroup:
            return self.node_groups.values()
        else:
            raise None

class UNet:
      def __init__(self, n):
            ''' n is the number of vertex '''
            self.nodes =  [None]*n
      
      def add_edge(self, source ,target):
            if self.nodes[source] == None:
                  self.nodes[source] = set()
            self.nodes[source].add(target)
            if self.nodes[target] == None:
                  self.nodes[target] = set()
            self.nodes[target].add(source)

      def common_verticis(self, v1, v2, min_v=0):
            neib1 = self.nodes[v1]
            neib2 = self.nodes[v2]
            if not neib1 or not neib2 or len(neib1)<min_v or len(neib2)<min_v:
                  return None
            comset = neib1 & neib2
            if len(comset)<min_v:
                  return None
            else:
                  return iter(comset)
      def connected(self, v1,v2):
          return self.nodes[v1] and (v2 in self.nodes[v1])
 
class Clique:
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
    def __iter__(self):
        for node in self.nodes:
            yield node
    def __hash__(self):
        if self.hash==None:
            self.hash=hash(reduce(lambda x,y:34*x+y, map(hash,self.nodes)))
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
    def getWeight(self, graph=None):
        if self.weight == None:
            #self.weight=self.intensity(graph)
            self.weight = max([graph[edge] for edge in itertools.combinations(self.nodes,2)])
        return self.weight     

    def intensity(self, graph):
        intens = 1
        for edge in itertools.combinations(self.nodes,2):
            intens *= graph[edge]
        return math.pow(intens, 1.0/len(self.nodes))

def findKCliques(unet, k, source, target):
    if k==2:
        yield Clique([source,target])
    else:
        vs = unet.common_verticis(source,target, min_v=k-2)
        if vs:
            if k==3:
                for v in vs: yield Clique([source,target,v])
            elif k==4:
                for v1,v2 in itertools.combinations(vs,2):
                    if unet.connected(v1,v2):
                        yield Clique([source,target,v1,v2])
            else:
                for k2vs in itertools.combinations(vs,k-2):
                    for v1,v2  in itertools.combinations(vs,2):
                        if not unet.connected(v1,v2): break
                    yield Clique([source,target] + list(k2vs))
    unet.add_edge(source,target)

 
def communities_scp(graph,k, min_nodes=10,min_alpha=0.2, min_beta=1.5):
    """ min_alpha represents minimum rate of nodes; 
    min_beta represents minumal value of largegroupsize to sumofgroupsize
    
    """
    unet=UNet(graph.vcount())
    edgelist = []
    for e in graph.es:
        edgelist.append(e)
    #sort in ascending order, pop up from the weightest edge
    edgelist.sort(key=lambda e:e['weight']) 

    ecnt = float(len(edgelist))
    epcnt = 0  # count of proccessed edges
    vpset = set()
    prelargest = 1
    k1tree = KCliqueTree()
    while edgelist:
        e = edgelist.pop()
        for c in findKCliques(unet,k,e.source,e.target):
            k1tree.union(list(c.getSubcliques()))
        vpset.add(e.source); vpset.add(e.target)
        epcnt += 1
        pvs = float(len(vpset))/graph.vcount()  # proccess eges proporation
        if pvs > min_alpha and prelargest>0 and k1tree.largest/float(prelargest) > min_beta:
            print 'critical edge weight of %d-clique: %f' % (k, e['weight'])
            break
        prelargest = k1tree.largest
        #print 'largest and second largest community:%d,%d' % (k1tree.largest, k1tree.seclargest)
        if pvs > 0.8 and k1tree.numOfGroup() <2:
            break
    nodecoms = [com for com in k1tree.getNodegroups() if len(com)>=min_nodes]
    return nodecoms


def comuid2name(graph, communities):
    """communities id to name"""
    com_names = []
    for com in communities:
        nameset = set()
        for nid in com:
            nameset.add(graph.vs[nid]['name'])
        com_names.append(nameset)
    return com_names


def comuname2id(graph,communities):
     """communities id to vertex's name"""
     com_ids = []
     for com in communities:
         idset = set()
         for name in com:
             idset.add(graph.vs.find(name).index)
         com_ids.append(idset)
     return com_ids


def communities_scp2(graph,k,min_nodes=12):
    unet=UNet(n=graph.vcount())
    cliquelist = []
    print 'finding %d-cliques...' % (k,)
    for e in graph.es:
        for clique in findKCliques(unet, k, e.source, e.target):
            cliquelist.append(clique)

    del unet
    print 'count of cliques: '+str(len(cliquelist))
    #sort in ascending order, pop up from the weightest clique
    cliquelist.sort(key=lambda x:x.getWeight(graph))
    
    print 'finding %d-communites...' % (k,)
    nodecoms = [com for com in findkCommunities(graph, cliquelist) if len(com)>=min_nodes]
    return nodecoms


                       
def findkCommunities(graph, cliquelist):
    ctree = KCliqueTree()
    #median = cliquelist[len(cliquelist)*4/5].getWeight(graph)
    while cliquelist:
        c = cliquelist.pop()  
        ctree.union(list(c.getSubcliques()))

        sgs = float(ctree.sumOfGroupSize())
        alpha = sgs/graph.vcount()
        beta = ctree.largest/sgs
        if alpha > 0.10 and beta > 0.5:
            break

    return ctree.getNodegroups()
