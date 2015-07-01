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
		self.roadWidth = 4 #default 4 meters from left to right lane


	def createLanes(self, roadWidth):

		self.roadWidth = roadWidth

		lanePointsA = []
		lanePointsB = []

		if len(self.xPoints) != len(self.yPoints):
			print ('X and Y points need to be equal! Stopping.')
			return
		else:

			for i in np.arange(len(self.xPoints)):
				factor = 1.0

				tangent = 0
				theta = 0

				if i == 0:
					point1b = [self.xPoints[i+1], self.yPoints[i+1]]
					point1a = [self.xPoints[i], self.yPoints[i]]

					tangent = self.getTangent(point1a, point1b)

					theta = np.arctan2(tangent[0], -tangent[1])

				elif i == (len(self.xPoints)-1):
					# point1b = [self.xPoints[i], self.yPoints[i]]
					# point1a = [self.xPoints[i-1], self.yPoints[i-1]]

					# tangent = self.getTangent(point1a, point1b)
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

					if dot > -0.97 and dot < 0.97:
						factor = 1.0 / np.sin(np.arccos(dot) * 0.5)

				# original gps point; center between two lane points
				gpsPtStart = [self.xPoints[i], self.yPoints[i]]
				
				pointA = [0,0]
				pointB = [0,0]

				# manually setting 4 as desired with for now
				width = (self.roadWidth * factor) * 0.5

				pointA[0] = gpsPtStart[0] + (np.cos(theta) * width)
				pointA[1] = gpsPtStart[1] + (np.sin(theta) * width)

				pointB[0] = gpsPtStart[0] - (np.cos(theta) * width)
				pointB[1] = gpsPtStart[1] - (np.sin(theta) * width)

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

		size[0] = boundarySize[0] * scalar
		size[1] = boundarySize[1] * scalar

		print ('Scaled Image Size:' + str(int(size[0])) + ' x ' + str(int(size[1])))

		# img = np.zeros((size[0],size[1],3) , np.uint8)
		if self.imgInitialized == False:
			if size[0] > size[1]:
				self.img = np.zeros((size[0],size[0],3) , np.uint8)
			else:
				self.img = np.zeros((size[1],size[1],3) , np.uint8)

			self.imgInitialized = True

		# drawing and inflating the middle lane.
		for midLane in centerLanes:

			xOffset = size[0]/2
			yOffset = size[1]/2

			

			# drawing second lane (A)
			for i in range(len(midLane[0])):

				# TODO: losing resolution of lanes with casting to int. 
				# i*2 is just downsampling the amount of lines drawn since you
				# would need really high resolution
				if i == 0:
					startPointX = (int(midLane[0][i]* scalar) ) + xOffset
					startPointY = (int(midLane[1][i]* scalar) ) + yOffset

					endPointX = (int(midLane[0][(i+1)]* scalar) ) + xOffset
					endPointY = (int(midLane[1][(i+1)]* scalar)) + yOffset
				elif i == (len(midLane[0])):
					# dont need to draw backwards
					break	
				else:			
					print midLane[0][i]
					startPointX = (int(midLane[0][i]* scalar)) + xOffset
					startPointY = (int(midLane[1][i]* scalar)) + yOffset

					print midLane[0][i-1]
					print
					endPointX = (int(midLane[0][(i-1)]* scalar)) + xOffset
					endPointY = (int(midLane[1][(i-1)]* scalar)) + yOffset

				cv2.line(self.img, (startPointX,startPointY), (endPointX,endPointY), (255,255,255), 60)

		# Drawing the side lanes
		for index, road in enumerate(roadLanes):

			xOffset = size[0]/2
			yOffset = size[1]/2

			# drawing second lane (A)
			for i in range(len(road[0])/2):

				# TODO: losing resolution of lanes with casting to int. 
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

		#cv2.imshow('image',self.img)
		cv2.imwrite('map1.png',self.img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		os.system('xdg-open ' + 'map1.png')

	def showImage(self):
		cv2.imshow('image',self.img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
