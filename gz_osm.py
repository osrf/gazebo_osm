#!/usr/bin/env python
import sys
sys.path.insert(0, 'source')
import os
import numpy as np
from lxml import etree
import argparse
from dict2sdf import GetSDF
from osm2dict import Osm2Dict
from getMapImage import getMapImage
from getOsmFile import getOsmFile
from roadSmoothing import SmoothRoad
from laneBoundaries import LaneBoundaries
import matplotlib.pyplot as plt
import math

TIMER = 1


def tic():
    #Homemade version of matlab tic and toc functions
    import time
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()


def toc():
    import time
    if 'startTime_for_tictoc' in globals():
        print ("Elapsed time is " + str(time.time()
               - startTime_for_tictoc)
               + " seconds.")
    else:
        print "Toc: start time not set"


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--outFile',
                    help='Output file name', type=str, default='outFile.sdf')
parser.add_argument('-o', '--osmFile', help='Name of the osm file generated',
                    type=str,
                    default='map.osm')
parser.add_argument('-O', '--inputOsmFile', help='Name of the Input osm file',
                    type=str,
                    default='')
parser.add_argument('-i', '--imageFile',
                    help='Generate and name .png image of the selected areas',
                    type=str,
                    default='')
parser.add_argument('-d', '--directory',
                    help='Output directory',
                    type=str,
                    default='./')
parser.add_argument('-l', '--lanes',
                    help='export image with lanes',
                    action='store_true')
parser.add_argument('-B', '--boundingbox',
                    help=('Give the bounding box for the area\n' +
                          'Format: MinLon MinLat MaxLon MaxLat'),
                    nargs='*',
                    type=float,
                    default=[-122.0129, 37.3596, -122.0102, 37.3614])

parser.add_argument('-r', '--roads',
                    help='Display Roads',
                    action='store_true')

parser.add_argument('-dbg', '--debug',
                    help='Debug Mode. Gazebo may take a while to load with this.',
                    action='store_true')

parser.add_argument('-m', '--models',
                    help='Display models',
                    action='store_true')

parser.add_argument('-b', '--buildings',
                    help='Display buildings',
                    action='store_true')

parser.add_argument('-a', '--displayAll',
                    help='Display roads and models',
                    action='store_true')
parser.add_argument('--interactive',
                    help='Starts the interactive version of the program',
                    action='store_true')

args = parser.parse_args()

flags = []

if args.buildings:
    flags.append('b')

if args.models:
    flags.append('m')

if args.roads:
    flags.append('r')

if args.lanes:
    flags.append('l')

if not(args.roads or args.models or args.buildings) or args.displayAll:
    flags.append('a')

if not os.path.exists(args.directory):
    os.makedirs(args.directory)

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
                           "Camino Real Highway, CA (2), Bethlehem," +
                           " PA (default=1): ")

        # if choice != '2': 
        #     startCoords = [37.3566, -122.0091]
        #     endCoords = [37.3574, -122.0081]

        # else:
        startCoords = [37.3596, -122.0129]
        endCoords = [37.3614, -122.0102]

    option = raw_input("Do you want to view the area specified? [Y/N]" +
                       " (default: Y): ").upper()

    osmFile = 'map.osm'
    args.boundingbox = [min(startCoords[1], endCoords[1]),
                        min(startCoords[0], endCoords[0]),
                        max(startCoords[1], endCoords[1]),
                        max(startCoords[0], endCoords[0])]

    if option != 'N':
        args.imageFile = 'map.png'

if args.inputOsmFile:
    f = open(args.inputOsmFile, 'r')
    root = etree.fromstring(f.read())
    f.close()
    args.boundingbox = [float(root[0].get('minlon')),
                        float(root[0].get('minlat')),
                        float(root[0].get('maxlon')),
                        float(root[0].get('maxlat'))]
if TIMER:
    tic()
print "Downloading the osm data ... "
osmDictionary = getOsmFile(args.boundingbox,
                           args.osmFile, args.inputOsmFile)
if TIMER:
    toc()

# if args.imageFile:
#     if TIMER:
#         tic()
#     print "Building the image file ..."
#     args.imageFile = args.directory + args.imageFile
#     getMapImage(args.osmFile, args.imageFile)
#     if TIMER:
#         toc()

#Initialize the class
if TIMER:
    tic()
osmRoads = Osm2Dict(args.boundingbox[0], args.boundingbox[1],
                    args.boundingbox[2], args.boundingbox[3],
                    osmDictionary, flags)

print "Extracting the map data for gazebo ..."
#get Road and model details
#roadPointWidthMap, modelPoseMap, buildingLocationMap = osmRoads.getMapDetails()
roadPointWidthMap = osmRoads.getRoadDetails()
if TIMER:
    toc()
if TIMER:
    tic()
print "Building sdf file ..."
#Initialize the getSdf class
sdfFile = GetSDF()


#Set up the spherical coordinates
sdfFile.addSphericalCoords(osmRoads.getLat(), osmRoads.getLon())
print ('Lat Center: '+ str(osmRoads.getLat()))
print ('Lon Center: '+ str(osmRoads.getLon()))

#add Required models
sdfFile.includeModel("sun")
# for model in modelPoseMap.keys():
#     points = modelPoseMap[model]['points']
#     sdfFile.addModel(modelPoseMap[model]['mainModel'],
#                      model,
#                      [points[0, 0], points[1, 0], points[2, 0]])

# for building in buildingLocationMap.keys():
#     sdfFile.addBuilding(buildingLocationMap[building]['mean'],
#                         buildingLocationMap[building]['points'],
#                         building,
#                         buildingLocationMap[building]['color'])

print ('')
print ('Number of Roads: ' + str(len(roadPointWidthMap.keys())))
print ('')

fig = plt.figure()

lanes = 0

roadLaneSegments = []

#Include the roads in the map in sdf file
for idx, road in enumerate(roadPointWidthMap.keys()):
    sdfFile.addRoad(road, roadPointWidthMap[road]['texture'])
    sdfFile.setRoadWidth(roadPointWidthMap[road]['width'], road)
    points = roadPointWidthMap[road]['points']

## insert bspline code here. do it *per* road line ##

    print ('')
    print ('Road: ' + road)


    xData = points[0, :]
    yData = points[1, :]

    if len(xData) < 3:
        print ('Cannot apply spline with [' + str(len(xData)) + '] points. At least 3 needed.')
        if len(xData) == 1:
            sdfFile.addRoadPoint([xData[0], yData[0], 0], road)
            sdfFile.addRoadDebug([xData[0], yData[0], 0], road)
            if len(xData) == 2:
                sdfFile.addRoadPoint([xData[1], yData[1], 0], road)
                sdfFile.addRoadDebug([xData[1], yData[1], 0], road)
    else:
        x = []

        for j in np.arange(len(xData)-1):
            if j != (len(xData)):

                

                if xData[j] > xData[j+1]:
                    # Decreasing. 
                    xDataNeg = [-1*xData[j], -1*xData[j+1]]
                    xTemp = []
                    res = 100

                    # Should only have two values, j and j+1
                    temp = np.linspace(xDataNeg[0], xDataNeg[1], res)

                    for t in np.arange(len(temp)):
                        if (j != 0) and (t == 0):
                            continue
                        else:
                            x.append(-temp[t])
                else:
                    # Increasing.
                    xTemp = []
                    res = 100

                    temp = np.linspace(xData[j], xData[j+1], res)

                    for t in np.arange(len(temp)):
                        if (j != 0) and (t == 0):
                            continue
                        else:
                            x.append(temp[t])                   


        hermite = SmoothRoad()

        eps = 0.0001

        xPts, yPts = hermite.simplify(xData, yData, eps)

        y = []
        for t in range(len(x)):
            if t != (len(x)-1):
                if x[t] < x[t+1]:
                    tension = 0.1
                    bias = 0.5
                    continuity = 0.5
                    increasing = True
                else:
                    tension = 0.5
                    bias = 0.0
                    continuity = -1.0
                    increasing = False
            for i in range(len(xPts) - 1):        
                if increasing:
                    if (xPts[i] <= x[t]) and (xPts[i+1] > x[t]):
                        break 
                else:
                    if (xPts[i] >= x[t]) and (xPts[i+1] < x[t]):
                        break                        
            deriv0, deriv1 = hermite.derivative(xPts, yPts, i, tension, bias, continuity)
            y.append(hermite.interpolate(xPts, yPts, i, deriv0, deriv1, x[t])) 

        eps = 0.0001

        xSimp, ySimp = hermite.simplify(x, y, eps)

        lanes = LaneBoundaries(xSimp, ySimp)

        [lanePointsA, lanePointsB]  = lanes.createLanes()

        roadLaneSegments.append([lanePointsA, lanePointsB])

        xPointsA = []
        yPointsA = []

        xPointsB = []
        yPointsB = []

        for i in range(len(lanePointsA)/2):
            xPointsA.append(lanePointsA[i*2][0])
            yPointsA.append(lanePointsA[i*2][1])
            #sdfFile.addLeftLaneDebug([lanePointsA[i*2][0], lanePointsA[i*2][1], 0], road)

            xPointsB.append(lanePointsB[i*2][0])
            yPointsB.append(lanePointsB[i*2][1])
            #sdfFile.addRightLaneDebug([lanePointsB[i*2][0], lanePointsB[i*2][1], 0], road)

        plt.plot(xData, yData, 'bo', x, y, 'r-', xPointsA, yPointsA, 'g-', xPointsB, yPointsB, 'g-')
        #plt.plot(xPointsA, yPointsA, 'g-', xPointsB, yPointsB, 'g-')
        #plt.plot(xData, yData, 'ro-', x, y, 'b+')
        ##plt.plot(x, y, 'b+')
        #plt.show()



        # lanes.saveImage(size, lanePointsA, lanePointsB)

        # if idx == len(roadPointWidthMap.keys())-1:
        #     lanes.showImage()

        for point in range(len(x)):
            sdfFile.addRoadPoint([x[point], y[point], 0], road)
            #sdfFile.addRoadDebug([x[point], y[point], 0], road)

    print ('-----------------------')

# if args.imageFile:
print "Generating the image file..."
size = osmRoads.getMapSize()
#    args.imageFile = args.directory + args.imageFile
#lanes.makeImage(size, 1, roadLaneSegments)

plt.show()

sdfFile.writeToFile(args.outFile)
if TIMER:
    toc()
