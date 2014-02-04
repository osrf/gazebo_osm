#!/usr/bin/env python
import sys
sys.path.insert(0, 'source')
from dict2sdf import GetSDF
from osm2dict import Osm2Dict
from getMapImage import getMapImage
from getOsmFile import getOsmFile

#get map coords
print("\nPlease enter the latitudnal and logitudnal" +
      " coordinates of the area or select from" +
      " default by hitting return twice \n")

startCoords = raw_input("Enter starting coordinates: [lon lat] :").split(' ')
endCoords = raw_input("Enter ending coordnates: [lon lat]: ").split(' ')

if startCoords and endCoords and len(startCoords) == 2 and len(endCoords) == 2:

    for incoords in range(2):

        startCoords[incoords] = float(startCoords[incoords])
        endCoords[incoords] = float(endCoords[incoords])

else:

    choice = raw_input("Default Coordinate options: West El" +
                       " Camino Highway, CA (default), Bethlehem, PA (2): ")

    if choice == '2':
        startCoords = [40.61, -75.382]
        endCoords = [40.608, -75.3714]

    else:
        startCoords = [37.385844, -122.101464]
        endCoords = [37.395664, -122.083697]

option = raw_input("Do you want to view the area specified? [Y/N]" +
                   " (default: Y) ").upper()

osmFile = 'map.osm'
osmDictionary = {}

getOsmFile([min(startCoords[1], endCoords[1]),
            min(startCoords[0], endCoords[0]),
            max(startCoords[1], endCoords[1]),
            max(startCoords[0], endCoords[0])],
           osmDictionary,
           osmFile)

if option != 'N':

    getMapImage(osmFile)


#Initialize the class
osmRoads = Osm2Dict(startCoords[1], startCoords[0], osmDictionary)

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
