import numpy as np
import matplotlib.pyplot as plt
import cv2
import math
import os

class LaneBoundaries:

	def __init__(self, xPoints, yPoints):
		self.xPoints = xPoints
		self.yPoints = yPoints
		# self.lanePoints = []

		self.imgInitialized = False
		self.img = 0
		self.roadWidth = 6 #default 6 meters from left to right lane

	# Code modeled off Road2d.cc from the Gazebo BitBucket
	def createLanes(self, roadWidth):

		self.roadWidth = roadWidth

		lanePointsA = []
		lanePointsB = []

		if len(self.xPoints) != len(self.yPoints):
			print ('X and Y points need to be equal! Stopping.')
			return
		else:

			# since xPoints and yPoints lengths are equal, you can use 
			# either lengths
			for i in np.arange(len(self.xPoints)):

				# initial scaling factor that is used to scale road width
				# at turns
				factor = 1.0

				# initial tangent vector (2D array) between two points
				tangent = 0

				# the angle between:
				# the tangent vector index i and i+1 
				# and
				# the tangent vector index i and i-1
				#
				# this angle later determines where the two side lane points will be 
				# positioned 
				theta = 0

				# first case is special, no index behind the current one
				if i == 0:
					point1b = [self.xPoints[i+1], self.yPoints[i+1]]
					point1a = [self.xPoints[i], self.yPoints[i]]

					tangent = self.getTangent(point1a, point1b)

					theta = np.arctan2(tangent[0], -tangent[1])

				elif i == (len(self.xPoints)-1):
					point1b = [self.xPoints[i], self.yPoints[i]]
					point1a = [self.xPoints[i-1], self.yPoints[i-1]]

					tangent = self.getTangent(point1a, point1b)
					break
				else:
					point2b = [self.xPoints[i+1], self.yPoints[i+1]]
					point2a = [self.xPoints[i], self.yPoints[i]]
					vector2 = self.getTangent(point2a, point2b)

					point1b = [self.xPoints[i], self.yPoints[i]]
					point1a = [self.xPoints[i-1], self.yPoints[i-1]]
					vector1 = self.getTangent(point1a, point1b)		

					# points[i+1] - points[i-1]
					point3b = [self.xPoints[i+1], self.yPoints[i+1]]
					point3a = [self.xPoints[i-1], self.yPoints[i-1]]
					tangent = self.getTangent(point3a, point3b)

					dot = np.dot(vector1, vector2 * -1)

					theta = np.arctan2(tangent[0], -tangent[1])

					# here we are considering a point to be colinear 
					# if it above +-0.97. If the dot product gives 
					# less then +-0.97, that means the lane is turning
					# so we need to adjust the width of the road with a 
					# new temporary factor
					if dot > -0.97 and dot < 0.97:
						factor = 1.0 / np.sin(np.arccos(dot) * 0.5)

				# original gps point; center between two lane points
				gpsPtStart = [self.xPoints[i], self.yPoints[i]]
				
				pointA = [0,0]
				pointB = [0,0]

				# width is considered to be the distance from the center point
				# to either of the side points. roadWidth/2 * factor
				width = (self.roadWidth * factor) * 0.5

				pointA[0] = gpsPtStart[0] + (np.cos(theta) * width)
				pointA[1] = gpsPtStart[1] + (np.sin(theta) * width)

				pointB[0] = gpsPtStart[0] - (np.cos(theta) * width)
				pointB[1] = gpsPtStart[1] - (np.sin(theta) * width)

				# store left and right lane points seperately
				lanePointsA.append(pointA)
				lanePointsB.append(pointB)

			return lanePointsA, lanePointsB


	def getTangent(self, point1, point2):
		point = np.array([point2[0]-point1[0], point2[1]-point1[1]])

		tangent = self.normalize(point)
		return tangent

	def normalize(self, vector):
		dist = np.sqrt(vector[0]*vector[0] + vector[1]*vector[1])

		if dist != 0:
			u = vector[0]/dist
			v = vector[1]/dist

			return np.array([u,v])
		else:
			return vector


	# size of image, scalar for pixel/meter, array containing all left and right road lane segments
	def makeImage(self, boundarySize, scalar, roadLanes, centerLanes):

		size = [0,0]

		if scalar <= 0:
			print ('Cannot scale image < 0 size! Setting to (boundarySize * 1).')
			scalar = 1
		# [0] = x, and [1] = y
		size[0] = boundarySize[0] * scalar
		size[1] = boundarySize[1] * scalar

		print ('| Scaled Size = [ ' + str(int(size[1])) + ' x ' + str(int(size[0])) + ' ] pixels')

		if self.imgInitialized == False:
			self.img = np.zeros((size[1], size[0], 3) , np.uint8)

			self.imgInitialized = True

		# drawing and inflating the middle lane.
		for midLane in centerLanes:

			xOffset = size[0]/2
			yOffset = size[1]/2


			if len(midLane[0]) > 2:

				# drawing second lane (A)
				for i in range(len(midLane[0])):

					# No downsample occurs for middle lane as it is thicker
					# and wont cause any rigged edges in the pixels of
					# the lines
					if i == 0:
						startPointX = (int(midLane[0][i]* scalar)) + xOffset
						startPointY = (int(midLane[1][i]* scalar)) + yOffset

						endPointX = (int(midLane[0][(i+1)]* scalar)) + xOffset
						endPointY = (int(midLane[1][(i+1)]* scalar)) + yOffset
					elif i == (len(midLane[0])):
						# dont need to draw backwards
						break	
					else:			

						startPointX = (int(midLane[0][i]* scalar)) + xOffset
						startPointY = (int(midLane[1][i]* scalar)) + yOffset

						endPointX = (int(midLane[0][(i-1)]* scalar)) + xOffset
						endPointY = (int(midLane[1][(i-1)]* scalar)) + yOffset

					# adding a line onto the overall entire image
					# line width as 60 is equal to 4 meters
					cv2.line(self.img, (startPointX,startPointY), (endPointX,endPointY), (255,255,255), 30)
			else:
				# If there is only one point, we can draw anything, so disregard it
				#print ('Road has LESS then four points!')
				# print len(midLane[0])

				if len(midLane[0]) == 2:
					# print len(midLane[0])
					startPointX = (int(midLane[0][0]* scalar) ) + xOffset
					startPointY = (int(midLane[1][0]* scalar) ) + yOffset
					endPointX = (int(midLane[0][1]* scalar) ) + xOffset
					endPointY = (int(midLane[1][1]* scalar)) + yOffset

					cv2.line(self.img, (startPointX,startPointY), (endPointX,endPointY), (255,255,255),30)

				elif len(midLane[0]) <= 4 and len(midLane[0]) > 1:
					startPointX = (int(midLane[0][0]* scalar) ) + xOffset
					startPointY = (int(midLane[1][0]* scalar) ) + yOffset
					endPointX = (int(midLane[0][1]* scalar) ) + xOffset
					endPointY = (int(midLane[1][1]* scalar)) + yOffset
					cv2.line(self.img, (startPointX,startPointY), (endPointX,endPointY), (255,255,255),30)

					startPointX = (int(road[0][1]* scalar) ) + xOffset
					startPointY = (int(road[1][1]* scalar) ) + yOffset
					endPointX = (int(road[0][2]* scalar) ) + xOffset
					endPointY = (int(road[1][2]* scalar)) + yOffset
					cv2.line(self.img, (startPointX,startPointY), (endPointX,endPointY), (255,255,255),30)


		# Drawing the side lanes
		for index, road in enumerate(roadLanes):

			# Setting the center of the image as the origin 
			# x = width/2
			# y = height/2
			xOffset = size[0]/2
			yOffset = size[1]/2

			# print ('Road # of points: ' + str(len(road[0])))

			if len(road[0]) > 4:
				
				# print ('Road has more then two points')

				# drawing second lane (A)
				# down sampling to draw every two road points, to not cause zig zags from pixel to pixel
				for i in range(len(road[0])/2):

					# i*2 is just downsampling the amount of lines drawn since you
					# would need really high resolution
					if i == 0:
						LstartPointX = (int(road[0][i*2][0]* scalar) ) + xOffset
						LstartPointY = (int(road[0][i*2][1]* scalar) ) + yOffset

						LendPointX = (int(road[0][(i+1)*2][0]* scalar) ) + xOffset
						LendPointY = (int(road[0][(i+1)*2][1]* scalar)) + yOffset
					elif i == (len(road[0])-1):
						# dont need to draw backwards
						break	
					else:				
						LstartPointX = (int(road[0][i*2][0]* scalar)) + xOffset
						LstartPointY = (int(road[0][i*2][1]* scalar)) + yOffset

						LendPointX = (int(road[0][(i-1)*2][0]* scalar)) + xOffset
						LendPointY = (int(road[0][(i-1)*2][1]* scalar)) + yOffset

					cv2.line(self.img, (LstartPointX,LstartPointY), (LendPointX,LendPointY), (255,255,255))


				# drawing second lane (B)	
				for i in range(len(road[1])/2):

					if i == 0:
						RstartPointX = (int(road[1][i*2][0]* scalar)) + xOffset
						RstartPointY = (int(road[1][i*2][1]* scalar)) + yOffset

						RendPointX = (int(road[1][(i+1)*2][0]* scalar)) + xOffset
						RendPointY = (int(road[1][(i+1)*2][1]* scalar)) + yOffset
					elif i == (len(road[1])-1):
						# dont need to draw backwards
						break	
					else:				
						RstartPointX = (int(road[1][i*2][0]* scalar)) + xOffset
						RstartPointY = (int(road[1][i*2][1]* scalar)) + yOffset

						RendPointX = (int(road[1][(i-1)*2][0]* scalar)) + xOffset
						RendPointY = (int(road[1][(i-1)*2][1]* scalar)) + yOffset

					cv2.line(self.img, (RstartPointX,RstartPointY), (RendPointX,RendPointY), (255,255,255))
			else:
				# If there is only one point, we can draw anything, so disregard it
				# print ('Road has LESS then four points!')
				# print len(road[0])
				# print road[0]

				if len(road[0]) == 2:
					for i in range(len(road[0])):
						LstartPointX = (int(road[0][0][0]* scalar) ) + xOffset
						LstartPointY = (int(road[0][0][1]* scalar) ) + yOffset
						LendPointX = (int(road[0][1][0]* scalar) ) + xOffset
						LendPointY = (int(road[0][1][1]* scalar)) + yOffset

						RstartPointX = (int(road[1][0][0]* scalar) ) + xOffset
						RstartPointY = (int(road[1][0][1]* scalar) ) + yOffset
						RendPointX = (int(road[1][1][0]* scalar) ) + xOffset
						RendPointY = (int(road[1][1][1]* scalar)) + yOffset

						cv2.line(self.img, (LstartPointX,LstartPointY), (LendPointX,LendPointY), (255,255,255))
						cv2.line(self.img, (RstartPointX,RstartPointY), (RendPointX,RendPointY), (255,255,255))
				elif len(road[0]) == 3:
						LstartPointX = (int(road[0][0][0]* scalar) ) + xOffset
						LstartPointY = (int(road[0][0][1]* scalar) ) + yOffset
						LendPointX = (int(road[0][1][0]* scalar) ) + xOffset
						LendPointY = (int(road[0][1][1]* scalar)) + yOffset
						cv2.line(self.img, (LstartPointX,LstartPointY), (LendPointX,LendPointY), (255,255,255))

						LstartPointX = (int(road[0][1][0]* scalar) ) + xOffset
						LstartPointY = (int(road[0][1][1]* scalar) ) + yOffset
						LendPointX = (int(road[0][2][0]* scalar) ) + xOffset
						LendPointY = (int(road[0][2][1]* scalar)) + yOffset
						cv2.line(self.img, (LstartPointX,LstartPointY), (LendPointX,LendPointY), (255,255,255))

						RstartPointX = (int(road[1][1][0]* scalar) ) + xOffset
						RstartPointY = (int(road[1][1][1]* scalar) ) + yOffset
						RendPointX = (int(road[1][2][0]* scalar) ) + xOffset
						RendPointY = (int(road[1][2][1]* scalar)) + yOffset
						
						cv2.line(self.img, (RstartPointX,RstartPointY), (RendPointX,RendPointY), (255,255,255))


		#cv2.imshow('image', self.img)

		imgInverted = np.zeros((size[1], size[0], 3) , np.uint8)
		imgInverted[:,:] = (255,255,255)

		imgGreyScale = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

		imgGreyScale = cv2.GaussianBlur(imgGreyScale,(5,5),0)

		edges = cv2.Canny(imgGreyScale, 100,200)

		ret,thresh = cv2.threshold(edges,25,255,cv2.THRESH_TOZERO)

		imgGreyScale = cv2.bitwise_not( thresh )

		imgGreyScale = cv2.transpose(imgGreyScale)
		imgGreyScale = cv2.flip(imgGreyScale,flipCode=-1)

		cv2.imwrite('map.png',imgGreyScale)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		os.system('xdg-open ' + 'map.png')
