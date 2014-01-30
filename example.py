#!/usr/bin/env python
from dict2sdf import GetSDF
from osm2dict import Osm2Dict

#Initialize the class
osmRoads = Osm2Dict()

#get Road and model details
roadPointWidthMap, modelPoseMap = osmRoads.getMapDetails()

#Initialize the getSdf class
sdfFile = GetSDF()


#Set up the spherical coordinates
sdfFile.addSphericalCoords(osmRoads.getLat(), osmRoads.getLon())

#add Required models
sdfFile.includeModel("sun")

for model in modelPoseMap.keys():
    points = modelPoseMap[model]['points']
    sdfFile.addModel(modelPoseMap[model]['mainModel'], model, [points[0, 0], points[1, 0], points[2, 0]])

#Include the roads in the map in sdf file
for road in roadPointWidthMap.keys():
    sdfFile.addRoad(road)
    sdfFile.setRoadWidth(roadPointWidthMap[road]['width'], road)
    points = roadPointWidthMap[road]['points']
    for point in range(len(points[0, :])):
        sdfFile.addRoadPoint([points[0, point], points[1, point], points[2, point]], road)

#output sdf File
sdfFile.writeToFile('outFile.sdf')
