from __future__ import division
#from PID import PID
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

	def getXAxis(self):
		length = len(self._errorAccum) - 1
		t = self.getControlTime()
		increment = t / length
		arr = [len(self._errorAccum)]
		s = 0
		print "t = ", t, " inc = ", increment, " length = ", length
		while s < (t - increment):
		 	arr.append(s)
		 	
		print "len of arr", len(arr)
		print "len of error = ", len(self._errorAccum) , " sum = ", s
		self.xAxis = arr
		return self.xAxis

	def _determineProportional(self, error):
		P = self.Kp*error
		#print "P = ", self.Kp, " * ", error, " = ", P
		return P;

	def _determineIntegral(self, _errorAccum):
		#print self.name, ": ", _errorAccum
		return self.Ki*sum(_errorAccum);
		

	def _determineDerivative(self, _errorAccum):
		l = len(_errorAccum)
		currentError = _errorAccum[l-1]
		previousError = _errorAccum[l-2]
		if currentError > 1:
			D = 1*self.Kd*(currentError - previousError)
			#D = 2*self.Kd*(currentError - previousError)
		else:
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

	def getxAxis(self):
		return self.xAxis;

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

	def _makeGUI(self):
		self.top = Tkinter.Tk()
		self.top.wm_title(self.name)
		self.top.geometry("300x300")
		B1 = Tkinter.Button(self.top, text ="+ Kp", command = self.incrKp)
		B2 = Tkinter.Button(self.top, text ="- Kp", command = self.decrKp)
		B3 = Tkinter.Button(self.top, text ="+ Ki", command = self.incrKi)
		B4 = Tkinter.Button(self.top, text ="- Ki", command = self.decrKi)
		B5 = Tkinter.Button(self.top, text ="+ kd", command = self.incrKd)
		B6 = Tkinter.Button(self.top, text ="- kd", command = self.decrKd)


		self.var1 = Tkinter.StringVar()
		self.var2 = Tkinter.StringVar()
		self.var3 = Tkinter.StringVar()

		label1 = Tkinter.Label( self.top, textvariable=self.var1)
		label2 = Tkinter.Label( self.top, textvariable=self.var2)
		label3 = Tkinter.Label( self.top, textvariable=self.var3)

		x1 = "Kp = ", self.Kp
		self.var1.set(x1)

		x2 = "Ki = ", self.Ki
		self.var2.set(x2)

		x3 = "Kd = ", self.Kd
		self.var3.set(x3)

		label1.pack()
		label2.pack()
		label3.pack()

		B1.pack()
		B2.pack()
		B3.pack()
		B4.pack()
		B5.pack()
		B6.pack()

		self.top.mainloop()

	def incrKp(self):
		self.setPGain(self.Kp + .1)
		x = "Kp = ", self.Kp
		self.var1.set(x)

	def decrKp(self):
		self.setPGain(self.Kp - .1)
		x = "Kp = ", self.Kp
		self.var1.set(x)

	def incrKi(self):
		self.setIGain(self.Ki + .1)
		x = "Ki = ", self.Ki
		self.var2.set(x)

	def decrKi(self):
		self.setIGain(self.Ki - .1)
		x = "Ki = ", self.Ki
		self.var2.set(x)

	def incrKd(self):
		self.setDGain(self.Kd + .1)
		x = "Kd = ", self.Kd
		self.var3.set(x)

	def decrKd(self):
		self.setDGain(self.Kd - .1)
		x = "Kd = ", self.Kd
		self.var3.set(x)





