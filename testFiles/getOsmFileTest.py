#! /usr/bin/env python
import unittest
import sys
sys.path.insert(0, '../source')
from getOsmFile import getOsmFile


class OsmFileTest(unittest.TestCase):

    def setUp(self):
        self.boxValid = [-75.385, 40.608, -75.378, 40.610]
        self.boxEmpty = []
        self.emptyFileName = ''
        self.fileName = 'myMap.osm'
        self.dataDict = {}

    def testEmptyName(self):
        self.assertTrue(getOsmFile(self.boxValid,
                                   self.dataDict,
                                   self.emptyFileName))
        self.dataDict.clear()

    def testEmptyBox(self):
        self.assertFalse(getOsmFile(self.boxEmpty,
                                    self.dataDict,
                                    self.fileName))
        self.dataDict.clear()


if __name__ == '__main__':
    unittest.main()
