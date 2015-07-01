import numpy as np
import matplotlib.pyplot as plt
import cv2
import math

class LaneBoundaries:

	def __init__(self, xPoints, yPoints):
		self.xPoints = xPoints
		self.yPoints = yPoints
		# self.lanePoints = []


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

	def saveImage(self, leftLane, rightLane):

		img = np.zeros((512,512,3), np.uint8)

		cv2.line(img,leftLane[0,1],leftLane[0,2],(255,0,0))

		cv2.imshow('image',img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
