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
import matplotlib.pyplot as plt

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
parser.add_argument('-B', '--boundingbox',
                    help=('Give the bounding box for the area\n' +
                          'Format: MinLon MinLat MaxLon MaxLat'),
                    nargs='*',
                    type=float,
                    default=[-122.0129, 37.3596, -122.0102, 37.3614])

parser.add_argument('-r', '--roads',
                    help='Display Roads',
                    action='store_true')

parser.add_argument('-s', '--spline',
                    help='Apply Cubic Spline for smoothing road corners',
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

if args.imageFile:
    if TIMER:
        tic()
    print "Building the image file ..."
    args.imageFile = args.directory + args.imageFile
    getMapImage(args.osmFile, args.imageFile)
    if TIMER:
        toc()

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

ppp = 0

#Include the roads in the map in sdf file
for road in roadPointWidthMap.keys():
    sdfFile.addRoad(road, roadPointWidthMap[road]['texture'])
    sdfFile.setRoadWidth(roadPointWidthMap[road]['width'], road)
    points = roadPointWidthMap[road]['points']

## insert bspline code here. do it *per* road line ##

    if ppp == 0:
        print (' ')
        print road

    # only applying 2d pchip for now
    

    for point in range(len(points[0, :])):

        #if i == 0:
            # print (' ')
            # print ('points[0, point] = ' + str(points[0, point]))
            # print ('points[1, point] = ' + str(points[1, point]))
            # print ('points[2, point] = ' + str(points[2, point]))
            # print (' ')

        sdfFile.addRoadPoint([points[0, point],
                            points[1, point],
                            points[2, point]],
                            road)
        sdfFile.addRoadDebug([points[0, point],
                              points[1, point],
                              points[2, point]],
                              road)
    if args.spline:
        xData = points[0, :]
        yData = points[1, :]

        print xData
        print yData

        #     +           -
        #   first   >   last
        if xData[0] > xData[-1]:
            xDataNeg = np.negative(xData)
            print ("xData[0] is greater then xData[-1]")
            #print xDataNeg
            x_neg = np.arange(xDataNeg[0], xDataNeg[-1], 0.01)
            x = np.negative(x_neg)
            increasing = False
        else:
            x = np.arange(xData[0], xData[-1], 0.5)
            increasing = True

        #x = np.linspace(xData[0], xData[-1], 100.0)
        if ppp == 0:
            ppp = ppp + 1

            print x

        hermite = SmoothRoad()

        tension = -0.1
        bias = 0.2
        continuity = -1.2
        eps = 0.1

        xPts, yPts = hermite.simplify(xData, yData, eps)

        # print ('[x]: ')
        # print ('' + str(np.array(xPts)))
        # print ('[y]: ')
        # print ('' + str(np.array(yPts)))

        y = []
        for t in x:
            print ('T:' + str(t))
            for i in range(len(xPts) - 1):
                if increasing:
                    #if (xPts[i] <= t):
                        #print ('xPts[' + str(xPts[i]) + '] is less then T at index [' + str(i) + ']')
                    if (xPts[i] <= t) and (xPts[i+1] > t):
                        #print ('xPts[' + str(xPts[i]) + '] is less then T: ' + str(t))
                        break
                else:
                    if (xPts[i] >= t) and (xPts[i+1] < t):
                        #print ('xPts[' + str(xPts[i]) + '] is less then T: ' + str(t))
                        break
            deriv0, deriv1 = hermite.derivative(xPts, yPts, i, tension, bias, continuity)
            y.append(hermite.interpolate(xPts, yPts, i, deriv0, deriv1, t)) 

        #print str(len(x))
        #print str(len(y))
        #plt.plot(xData, yData, 'ro-', x, y, 'b+')
        plt.plot(x, y, 'b+')
        plt.show()

#output sdf File
sdfFile.writeToFile(args.outFile)
if TIMER:
    toc()
