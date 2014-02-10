#!/usr/bin/env python
import unittest
from lxml import etree
import os
import sys
sys.path.insert(0, '../source')

from getOsmFile import getOsmFile
from osm2dict import Osm2Dict
from dict2sdf import GetSDF


class GetSDFTest(unittest.TestCase):

    def setUp(self):
        osmDict = {}
        osmDict = getOsmFile([-75.93, 40.61, -75.90, 40.62], 'map.osm')
        osmRoads = Osm2Dict(-75.93, 40.61, osmDict)
        roadPointWidthMap, modelPoseMap = osmRoads.getMapDetails()

        #Initialize the getSdf class
        sdfFile = GetSDF()

        #Set up the spherical coordinates
        sdfFile.addSphericalCoords(osmRoads.getLat(), osmRoads.getLon())

        #add Required models
        sdfFile.includeModel("sun")

        for model in modelPoseMap.keys():
            points = modelPoseMap[model]['points']
            sdfFile.addModel(modelPoseMap[model]['mainModel'],
                             model,
                             [points[0, 0], points[1, 0], points[2, 0]])

        #Include the roads in the map in sdf file
        for road in roadPointWidthMap.keys():
            sdfFile.addRoad(road)
            sdfFile.setRoadWidth(roadPointWidthMap[road]['width'], road)
            points = roadPointWidthMap[road]['points']
            for point in range(len(points[0, :])):
                sdfFile.addRoadPoint([points[0, point],
                                      points[1, point],
                                      points[2, point]],
                                     road)

        #output sdf File
        sdfFile.writeToFile('outFile.sdf')

    def validateSchema(self):
        try:
            with open('outFile.sdf', 'r') as f:
                etree.fromstring(f.read(),
                                 base_url=
                                 "http://sdformat.org/schemas/world.xsd")
            return True
        except:
            return False

    def gzCheck(self):
        return os.system('gzsdf check outFile.sdf')

    def testXMLSchema(self):
        self.assertTrue(self.validateSchema())

    def testGzSDF(self):
        self.assertEqual(self.gzCheck(), 0)


if __name__ == '__main__':
    unittest.main()
