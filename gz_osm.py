#!/usr/bin/env python
import sys
sys.path.insert(0, 'source')
import argparse
from dict2sdf import GetSDF
from osm2dict import Osm2Dict
from getMapImage import getMapImage
from getOsmFile import getOsmFile


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--outFile',
                    help='Output file name', type=str, default='outFile.sdf')
parser.add_argument('-o', '--osmFile', help='Name of the osm file', type=str,
                    default='map.osm')
parser.add_argument('-m', '--imageFile',
                    help='Generate and name .png image of the selected areas',
                    type=str,
                    default='')
parser.add_argument('-d', '--directory',
                    help='Output directory',
                    type=str,
                    default='./')
parser.add_argument('-b', '--boundingbox',
                    help=('Give the bounding box for the area' +
                          'Format: MinLon MinLat MaxLon MaxLat'),
                    nargs='*',
                    type=float,
                    default=[-75.382, 40.608, -75.377, 40.610])

args = parser.parse_args()

args.osmFile = args.directory + args.osmFile
args.imageFile = args.directory + args.imageFile
args.outFile = args.directory + args.outFile

osmDictionary = {}

getOsmFile(args.boundingbox,
           osmDictionary,
           args.osmFile)

if args.imageFile:

    getMapImage(args.osmFile, args.imageFile)


#Initialize the class
osmRoads = Osm2Dict(args.boundingbox[0], args.boundingbox[1], osmDictionary)

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
sdfFile.writeToFile(args.outFile)
