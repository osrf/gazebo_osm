import numpy as np
import unittest
import sys
sys.path.insert(0, '../source')

from osm2dict import Osm2Dict
from getOsmFile import getOsmFile


class Osm2DictTest(unittest.TestCase):

    def setUp(self):
        self.osmDict = {}
        getOsmFile([-75.93, 40.61, -75.90, 40.62], self.osmDict, 'map.osm')
        self.testClass = Osm2Dict(0, 0, self.osmDict)

    def testDist(self):
        self.assertEqual(round(self.testClass.latLonDist([[1, 1]]), 2), 157.25)

    def testDistEmpty(self):
        self.assertEqual(self.testClass.latLonDist([]), 0)

    def testBearing(self):
        self.assertEqual(round(self.testClass.latLongBearing([[1, 1]]), 2),
                         0.79)

    def testBearingEmpty(self):
        self.assertEqual(self.testClass.latLongBearing([]), 0)

    def testPointsEmpty(self):
        self.assertEqual(self.testClass.getPoints([]), [])

    def testPoints(self):
        self.assertEqual(self.testClass.getPoints([[1, 1]]).all(),
                         np.array([[111200.57170516],
                                   [111183.63531948],
                                   [0.]]).all())

if __name__ == '__main__':
    unittest.main()
