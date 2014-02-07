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
parser.add_argument('-i', '--imageFile',
                    help='Generate and name .png image of the selected areas',
                    type=str,
                    default='')
parser.add_argument('-d', '--directory',
                    help='Output directory',
                    type=str,
                    default='./')
parser.add_argument('-b', '--boundingbox',
                    help=('Give the bounding box for the area\n' +
                          'Format: MinLon MinLat MaxLon MaxLat'),
                    nargs='*',
                    type=float,
                    default=[-75.380, 40.606, -75.377, 40.609])

parser.add_argument('-r', '--roads',
                    help='Display Roads',
                    action='store_true')

parser.add_argument('-m', '--models',
                    help='Display models and building',
                    action='store_true')

parser.add_argument('-a', '--displayAll',
                    help='Display roads and models',
                    action='store_true')
parser.add_argument('--interactive',
                    help='Starts the interactive version of the program',
                    action='store_true')

args = parser.parse_args()

flags = []

if args.models:
    flags.append('m')

if args.roads:
    flags.append('r')

if not(args.roads) and not(args.models) or args.displayAll:
    flags.append('a')

args.osmFile = args.directory + args.osmFile
args.outFile = args.directory + args.outFile

osmDictionary = {}

if args.interactive:
    print("\nPlease enter the latitudnal and logitudnal" +
          " coordinates of the area or select from" +
          " default by hitting return twice \n")

    startCoords = raw_input("Enter starting coordinates: " +
                            "[lon lat] :").split(' ')
    endCoords = raw_input("Enter ending coordnates: [lon lat]: ").split(' ')

    if (startCoords and endCoords and
            len(startCoords) == 2 and len(endCoords) == 2):

        for incoords in range(2):

            startCoords[incoords] = float(startCoords[incoords])
            endCoords[incoords] = float(endCoords[incoords])

    else:

        choice = raw_input("Default Coordinate options: West El " +
                           "Camino Highway, CA (default), Bethlehem, PA (2): ")

        if choice == '2':
            startCoords = [40.61, -75.382]
            endCoords = [40.608, -75.3714]

        else:
            startCoords = [37.385844, -122.101464]
            endCoords = [37.395664, -122.083697]

    option = raw_input("Do you want to view the area specified? [Y/N]" +
                       " (default: Y): ").upper()

    osmFile = 'map.osm'

    args.boundingbox = [min(startCoords[1], endCoords[1]),
                        min(startCoords[0], endCoords[0]),
                        max(startCoords[1], endCoords[1]),
                        max(startCoords[0], endCoords[0])]

    if option != 'N':
        args.imageFile = 'map.png'

osmDictionary = getOsmFile(args.boundingbox,
                           args.osmFile)

if args.imageFile:

    args.imageFile = args.directory + args.imageFile
    getMapImage(args.osmFile, args.imageFile)

#Initialize the class
osmRoads = Osm2Dict(args.boundingbox[0], args.boundingbox[1],
                    osmDictionary, flags)

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
