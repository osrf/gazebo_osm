import unittest
import sys
sys.path.insert(0, '../source')
from getMapImage import getMapImage


class MapImageTest(unittest.TestCase):

    def testPass(self):
        self.assertEqual(getMapImage('map.osm'), 0)

    def testFail(self):
        self.assertEqual(getMapImage(''), -1)

if __name__ == '__main__':
    unittest.main()
