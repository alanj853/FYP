"""
Class for creating and implementing PID controllers
"""

from __future__ import division
from threading import Thread
from Plotter import Plotter

import Tkinter
import matplotlib 
import time
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

class PIDController:

	
	def __init__(self, controllerName):
		self.name = controllerName
		print "PID Controller Created. Name = ", self.name
		name = "Plot for PID controller ", self.name
		self._errorAccum = [0]
		self._incAccum = [0]
		self.xAxis = [0]
		self.Kp = 0;
		self.Ki = 0;
		self.Kd = 0;
		self.maxError = 0
		self.minError = 0
		self.maxInc = 2500
		self.minInc = -1*self.maxInc
		self.count = 0
		self.errorThreshold = 0.25
		self.lastError = 0
		self.percentageOvershoot = 0
		self.settlingTime = 0;
		self.controlTime = 0
		self.startTime = 0
		

	def _determineIncrement(self, target, current):
		error = target - current;
		#print "IN ", self.name, " : ", target , " - ", current, " = " , error
		self.lastError = error
		if abs(error) < self.errorThreshold:
			error = 0
		self._errorAccum.append(error)
		
		P = self._determineProportional(error)
		I = self._determineIntegral(self._errorAccum)
		D = self._determineDerivative(self._errorAccum)
		#print "Controller ", self.name, ": For Error = ", error ,", P = ", P, " I = ", I, " D = ", D

		inc = P + I + D

		if inc > self.maxInc:
			inc = self.maxInc
		if inc < self.minInc:
			inc = self.minInc

		self._incAccum.append(inc)
		return inc


	def getLastError(self):
		return self.lastError



	## function to deterine proportional component
	def _determineProportional(self, error):
		P = self.Kp*error
		#print "P = ", self.Kp, " * ", error, " = ", P
		return P;

		
	## function to deterine integral component
	def _determineIntegral(self, _errorAccum):
		#print self.name, ": ", _errorAccum
		#return self.Ki*sum(_errorAccum); ## integrate over error from time '0'

		## this method only integrates over area where error last crossed X axis
		## so doesn't include all error "history" in calculation
		currErrorAccum = [] ## list to store error
		if self.lastError > 0:
			i = len(self._errorAccum) - 1
			while i >= 0:
				x = self._errorAccum[i]
				if x > 0:
					currErrorAccum.append(x)
				else:
					break;
				i = i -1
		elif self.lastError < 0:
			i = len(self._errorAccum) - 1
			while i >= 0:
				x = self._errorAccum[i]
				if x < 0:
					currErrorAccum.append(x)
				else:
					break;
				i = i -1
		else:
			currErrorAccum.append(0)

		return self.Ki*sum(currErrorAccum);


		
	## function to deterine derivative component
	def _determineDerivative(self, _errorAccum):
		l = len(_errorAccum)
		currentError = _errorAccum[l-1]
		previousError = _errorAccum[l-2]
		D = 1*self.Kd*(currentError - previousError)
		#print "D = ", self.Kd, " * (", currentError , " - ", previousError, ") = ", D
		return D; ## will return current slope

	def reset(self):
		self._errorAccum = [0]
		self._incAccum = [0]
		self.startTime = time.time()
		#print "new len = ", len(self._errorAccum)

	def getControlTime(self):
		if self.startTime == 0: ## if controller was never put into auto pilot
			self.controlTime = 0
		else:
			self.controlTime = time.time() - self.startTime
		return self.controlTime

	def getErrorAccum(self):
		return self._errorAccum;

	def getIncAccum(self):
		return self._incAccum;

	def getMaxError(self):
		return self.maxError

	def getMinError(self):
		return self.minError

	def setMaxInc(self, x):
		self.maxInc = x
		self.minInc = -1*x

	def setMaxError(self, x):
		self.maxError = x

	def setMinError(self, x):
		self.minError = x

	def setPGain(self, x):
		self.Kp = x
		print "P Gain = ", self.Kp

	def setIGain(self, x):
		self.Ki = x
		print "I Gain = ", self.Ki

	def setDGain(self, x):
		self.Kd = x
		print "D Gain = ", self.Kd

	def setErrorThreshold(self, x):
		self.errorThreshold = x






