import numpy as np
import matplotlib.pyplot as plt

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
			print ('xPoints:')
			print self.xPoints
			print ('yPoints:')
			print self.yPoints
			for i in np.arange(len(self.xPoints)):
				factor = 1.0

				if i == 0:
					point1b = [self.xPoints[i+1], self.yPoints[i+1]]
					point1a = [self.xPoints[i], self.yPoints[i]]

					print ('')
					print point1a
					print point1b
					print ('')

					tangent = self.getTangent(point1a, point1b)

				elif i == (len(self.xPoints) - 1):
					point1b = [self.xPoints[i], self.yPoints[i]]
					point1a = [self.xPoints[i-1], self.yPoints[i-1]]

					tangent = self.getTangent(point1a, point1b)

				else:
					point2b = [self.xPoints[i+1], self.yPoints[i+1]]
					point2a = [self.xPoints[i], self.yPoints[i]]
					vector2 = self.getTangent(point2a, point2b)

					point1b = [self.xPoints[i], self.yPoints[i]]
					point1a = [self.xPoints[i-1], self.yPoints[i-1]]
					vector1 = self.getTangent(point1a, point1b)		

					# points[i+1] - points[i-1]
					tangent = self.getTangent(point1a, point2b)

					dot = np.dot(vector1, vector2 * -1)

					print ('Dot:')
					print dot
					print ('')

					if dot > -0.97 and dot < 0.97:
						factor = 1.0 / np.sin(np.arccos(dot) * 0.5)

				theta = np.arctan2(tangent[0], -tangent[1])

				print ('Theta:')
				print theta
				print ('')

				# original gps point; center between two lane points
				gpsPtStart = [self.xPoints[i], self.yPoints[i]]
				
				pointA = [0,0]
				pointB = [0,0]

				# manually setting 4 as desired with for now
				width = (4 * factor) * 0.5

				#print ('cos*width: ' + str(np.cos(theta) * width))
				#print ('pointA[0]: ' + str(pointA[0]))
				#print ('equals   : ' + str((pointA[0]) + (np.cos(theta) * width)))

				print gpsPtStart[0]
				pointA[0] = gpsPtStart[0] + (np.cos(theta) * width)
				pointA[1] = gpsPtStart[1] + (np.sin(theta) * width)

				pointB[0] = gpsPtStart[0] - (np.cos(theta) * width)
				pointB[1] = gpsPtStart[1] - (np.sin(theta) * width)

				#print ('PointA (x,y): [' + str(pointA[0]) + ',' + str(pointA[1]) + ']')

				lanePointsA.append(pointA)
				lanePointsB.append(pointB)
				# np.append(lanePointsA, pointA)
				# np.append(lanePointsB, pointB)
				# lanePointsA.append(pointA, axis=0)
				# lanePointsB.append(pointB, axis=0)
				#lanePoints.append(np.array([pointA, pointB]))

			print ('Lane Points: ')
			print ('A:')
			print lanePointsA
			print ('B:')
			print lanePointsB

			return lanePointsA, lanePointsB


	def getTangent(self, point1, point2):
		point = np.array([point2[0]-point1[0], point2[1]-point1[1]])

		tangent = self.normalize(point)
		return tangent

	def normalize(self, vector):
		dist = np.sqrt(vector[0]*vector[0] + vector[1]*vector[1])

		print ('dist: ' + str(dist))

		if dist != 0:
			u = vector[0]/dist
			v = vector[1]/dist

			print('')
			print('U:')
			print u
			print('V:')
			print v
			print('')

			return np.array([u,v])
		else:
			return vector


if __name__ == "__main__":
	xData = [0.5, 1., 1.5, 1.75, 3., 6., 6.25, 8.]
	yData = [-2.5,-2.,-1.5,-1,1,2,3,3.5]

	lanes = LaneBoundaries(xData, yData)

	[lanePointsA, lanePointsB]  = lanes.createLanes()

	xPointsA = []
	yPointsA = []

	xPointsB = []
	yPointsB = []

	for i in range(len(lanePointsA)):
		xPointsA.append(lanePointsA[i][0])
		yPointsA.append(lanePointsA[i][1])

		xPointsB.append(lanePointsB[i][0])
		yPointsB.append(lanePointsB[i][1])

	# print xPointsA
	# print ('--')
	# print yPointsA

	plt.plot(xData, yData, 'ro-', xPointsA, yPointsA, 'b+', xPointsB, yPointsB, 'g+')
	#plt.plot(x, y, 'b+')
	plt.show()
