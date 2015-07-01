import numpy as np
import matplotlib.pyplot as plt
import cv2
import math

class LaneBoundaries:

	def __init__(self, xPoints, yPoints):
		self.xPoints = xPoints
		self.yPoints = yPoints
		# self.lanePoints = []

		self.imgInitialized = False
		self.img = 0


	def createLanes(self):

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
				width = (4 * factor) * 0.5

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

	# def saveImage(self, size, leftLane, rightLane):

	# 	# img = np.zeros((size[0],size[1],3) , np.uint8)
	# 	if self.imgInitialized == False:
	# 		if size[0] > size[1]:
	# 			self.img = np.zeros((size[0],size[0],3) , np.uint8)
	# 		else:
	# 			self.img = np.zeros((size[1],size[1],3) , np.uint8)

	# 		self.imgInitialized = True

	# 	xOffset = size[0]/2
	# 	yOffset = size[1]/2

	# 	# drawing second lane (A)
	# 	for i in range(len(leftLane)/2):
	# 		LstartPointX = int(leftLane[i*2][0]) + xOffset
	# 		LstartPointY = int(leftLane[i*2][1]) + yOffset

	# 		LendPointX = int(leftLane[i*2][0]) + xOffset
	# 		LendPointY = int(leftLane[i*2][1]) + yOffset

	# 		cv2.line(self.img, (LstartPointX,LstartPointY), (LendPointX,LendPointY), (255,255,255))


	# 	# drawing second lane (B)	
	# 	for i in range(len(rightLane)/2):
	# 		RstartPointX = int(leftLane[i*2][0]) + xOffset
	# 		RstartPointY = int(leftLane[i*2][1]) + yOffset

	# 		RendPointX = int(leftLane[i*2][0]) + xOffset
	# 		RendPointY = int(leftLane[i*2][1]) + yOffset

	# 		cv2.line(self.img, (RstartPointX,RstartPointY), (RendPointX,RendPointY), (255,255,255))

	# size of image, scalar for pixel/meter, array containing all left and right road lane segments
	def makeImage(self, size, scalar, roads):

		# img = np.zeros((size[0],size[1],3) , np.uint8)
		if self.imgInitialized == False:
			if size[0] > size[1]:
				self.img = np.zeros((size[0],size[0],3) , np.uint8)
			else:
				self.img = np.zeros((size[1],size[1],3) , np.uint8)

			self.imgInitialized = True

		for index, road in enumerate(roads):
			print ('Index: ' + str(index))


			xOffset = size[0]/2
			yOffset = size[1]/2

			# drawing second lane (A)
			for i in range(len(road[0])):

				if i == 0:
					LstartPointX = int(road[0][i][0]) + xOffset
					LstartPointY = int(road[0][i][1]) + yOffset

					LendPointX = int(road[0][i+1][0]) + xOffset
					LendPointY = int(road[0][i+1][1]) + yOffset
				elif i == (len(road[0])-1):
					# dont need to draw backwards
					break	
				else:				
					LstartPointX = int(road[0][i][0]) + xOffset
					LstartPointY = int(road[0][i][1]) + yOffset

					LendPointX = int(road[0][i-1][0]) + xOffset
					LendPointY = int(road[0][i-1][1]) + yOffset

				cv2.line(self.img, (LstartPointX,LstartPointY), (LendPointX,LendPointY), (255,255,255))


			# drawing second lane (B)	
			for i in range(len(road[1])):

				if i == 0:
					RstartPointX = int(road[1][i][0]) + xOffset
					RstartPointY = int(road[1][i][1]) + yOffset

					RendPointX = int(road[1][i+1][0]) + xOffset
					RendPointY = int(road[1][i+1][1]) + yOffset
				elif i == (len(road[1])-1):
					# dont need to draw backwards
					break	
				else:				
					RstartPointX = int(road[1][i][0]) + xOffset
					RstartPointY = int(road[1][i][1]) + yOffset

					RendPointX = int(road[1][i-1][0]) + xOffset
					RendPointY = int(road[1][i-1][1]) + yOffset

				cv2.line(self.img, (RstartPointX,RstartPointY), (RendPointX,RendPointY), (255,255,255))

		cv2.imshow('image',self.img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def showImage(self):
		cv2.imshow('image',self.img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
