##############################################################################
#Author: Krystian Gebis
#Version: 1.0
#Package: gazebo_osm
#
#Description: SmoothRoads() class
#             Implements function for smoothing road corners, intersections,
#             and wavy roads.
##############################################################################
from decimal import *
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.hermite import hermfit, hermval
from dp import simplify_points

from scipy import interpolate

class SmoothRoad:

	"""
		Args:
		    x, y (array): Input points to be interpolated between
		    i (index): Index of arrays to use
		    deriv0, deriv1 (array): derivative of curve at points
		Returns:
		    point (array): interpolated point

		math:: p(t) = p_0 H_0^3(t) + m_0 H_1^3(t) + m_1 H_2^3(t) + p_1 H_3^3(t)
	"""
	def interpolate(self, x, y, i, deriv0, deriv1, absis):
		t = (absis - x[i]) / (x[i+1] - x[i])
		point = (2*t**3 - 3*t**2 + 1)*y[i] + (t**3 - 2*t**2 + t)*deriv0\
			+ (-2*t**3 + 3*t**2)*y[i+1] + (t**3 - t**2)*deriv1
		print point
		return point


		"""This function calculates the Kochanek--Bartels spline   
		    Args:
		        x, y (array): Input points to be interpolated between
		        tension (float): (t)ension or roundness of curve
		        bias (float):  (b)ias or shoot of curve
		        continuity (float): (c)ontinuity or corners of curve
		            
		    Returns:
		        deriv0, deriv1 (array): derivatives at p0 and p1 (x[i], x[i+1])
		            
		    math:: d_i = \frac{(1-t) (1+b) (1+c)}{2} (p_i - p_{i-1}) + frac{(1-t) (1-b) (1-c)}{2} (p_{i+1} - p_i)
		    math:: d_{i+1} = \frac{(1-t) (1+b) (1-c)}{2} (p_{i+1} - p_i) + frac{(1-t) (1-b) (1+c)}{2} (p_{i+2} - p_{i+1})
	    """
	def derivative(self, x, y, i, tension, bias, continuity):
		if i == 0:
			deriv0 = (y[1] - y[0])
			deriv1 = (y[2] - y[0]) / 2.0
		elif i == len(x) - 2:
			deriv0 = (y[i+1] - y[i-1]) / 2.0
			deriv1 = (y[i+1] - y[i])
		else:
			deriv0 = ((1-tension)*(1+bias)*(1+continuity))*(y[i]-y[i-1])/2\
			+ ((1-tension)*(1-bias)*(1-continuity))*(y[i+1]-y[i])/2
			deriv1 = ((1-tension)*(1+bias)*(1-continuity))*(y[i+1]-y[i])/2\
			+ ((1-tension)*(1-bias)*(1+continuity))*(y[i+2]-y[i+1])/2
		# Consider precalculating for speed
		return deriv0, deriv1

	def simplify(self, xData, yData, eps):
		pts = []
		for item in np.arange(len(xData)):
			pts.append((xData[item], yData[item]))

		# print ('[x,y]: ')
		# print ('' + str(np.array(pts)))

		pts = simplify_points(pts, eps)

		# print ('[xS,yS]: ')
		# print ('' + str(np.array(pts)))

		xPts = []
		yPts = []
		for item in np.arange(len(pts)):
			xPts.append(pts[item][0])
			yPts.append(pts[item][1])

		# print ('[x]: ')
		# print ('' + str(np.array(xPts)))
		# print ('[y]: ')
		# print ('' + str(np.array(xPts)))

		xPts = np.array(xPts)
		yPts = np.array(yPts)
		return xPts, yPts