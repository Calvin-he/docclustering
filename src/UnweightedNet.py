import array, bisect

class UnweightedNet:
      def _init__(self, n):
            ''' n is the number of vertex '''
            self.nodes =  [None for i in range(0,n)]
      
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
            if neib1 or neib2: return None
            if len(neib1)< min_v or len(neib2) < min_v:
                  return None
            comset = neib1 & neib2
            if len(com_set)<min_v:
                  return None
            else:
                  return tuple(comset)

      def degree(self, v):
            return len(self.nodes[v]) if self.noes[v] else return 0

      
