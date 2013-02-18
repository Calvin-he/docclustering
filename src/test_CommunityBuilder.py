import unittest
from CommunityBuilder import CommunityBuilder

class CommunityBuilderTest(unittest.TestCase):
    
    def setUp(self):
        self.cb = CommunityBuilder('../data/cn-topic.db')

    def test_load_title_wordnet(self):
        g = self.cb.load_title_wordnet()
        print 'count of vertex and eges: %d, %d' %(g.vcount(),g.ecount())


if __name__ == '__main__':
    unittest.main()
