import numpy as np
import unittest
import sys
sys.path.insert(0, '../source')

from osm2dict import Osm2Dict
from getOsmFile import getOsmFile


class Osm2DictTest(unittest.TestCase):

    def setUp(self):
        self.osmDict = {}
        self.osmDict = getOsmFile([-75.38, 40.606, -75.377, 40.609], 'map.osm')
        self.testClass = Osm2Dict(-75.93, 40.61, self.osmDict)

    def testDist(self):
        self.assertEqual(round(self
                               .testClass
                               .latLonDist(np.array([[-75.83, 41.61]])), 2),
                         111.51)

    def testDistEmpty(self):
        self.assertEqual(self.testClass.latLonDist(np.array([])), 0)

    def testBearing(self):
        self.assertEqual(round(self
                               .testClass
                               .latLongBearing(np.array([[-75.83, 41.61]])),
                               2),
                         0.07)

    def testBearingEmpty(self):
        self.assertEqual(self.testClass.latLongBearing(np.array([])), 0)

    def testPointsEmpty(self):
        self.assertEqual(self.testClass.getPoints(np.array([])), [])

    def testPoints(self):
        self.assertEqual(self
                         .testClass
                         .getPoints(np.array([[-75.83, 41.61]])).all(),
                         np.array([[111200.57170516],
                                   [111183.63531948],
                                   [0.]]).all())

    def testNumRoadsModels(self):
        roadList, modelsList = self.testClass.getMapDetails()
        self.assertEqual(len(roadList.keys()), 95)
        self.assertEqual(len(modelsList.keys()), 40)

    def testSetGetFlags(self):
        self.testClass.setFlags('m')
        self.assertEqual(self.testClass.getFlags(), ['m'])

    def testModels(self):
        self.testClass.setFlags('m')
        roadList, modelsList = self.testClass.getMapDetails()
        self.assertEqual(len(roadList.keys()), 0)
        self.assertEqual(len(modelsList.keys()), 40)

    def testRoads(self):
        self.testClass.setFlags('r')
        roadList, modelsList = self.testClass.getMapDetails()
        self.assertEqual(len(roadList.keys()), 95)
        self.assertEqual(len(modelsList.keys()), 0)

if __name__ == '__main__':
    unittest.main()
