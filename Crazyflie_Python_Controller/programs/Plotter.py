from datetime import datetime, date
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.animation as animation
from SubPlot import SubPlot


class Plotter():

	_plotData = True
	_closePlot = False
	X1 = []
	Y1 = []
	XMin1 = 0
	XMax1 = 0
	YMin1 = 0
	YMax1 = 0
	YLabel1 = ""
	XLabel1 = ""

	def __init__(self, title):
		print "Plot object '", title, "' created"
		self._title = title

	def plot(self):
		self.fig = plt.figure()
		self.ax1 = self.fig.add_subplot(1,1,1)
		self.ax1.set_title(self._title)

		ani = animation.FuncAnimation(self.fig, self.update, interval=100)

 		plt.show()

	def update(self,i):
		plt.cla()

		self.ax1.plot(self.Y1)

	def closePlot(self):
		plt.close()

	

	















	def _old_plot_data(self):
		X = []
		X2 = []
		Y = self.pidctrl.getErrorAccum()
		thrustArray = []
		x = 0
		#f,lines = plt.subplots(2, sharex=True)
		f, (ax1, ax2) = plt.subplots(2,1)

		plt.ion()
		graph1 = ax1.plot([0],Y)[0]
		graph2 = ax2.plot([0],Y)[0]
		xMin = 0
		xMax = len(le.pidctrl.getErrorAccum())
		yMin = -5 #le.pidctrl.getMinError()
		yMax = 5 #le.pidctrl.getMaxError()
		plt.axis([xMin, xMax, yMin, yMax])
		plt.title(self._title)
		plt.xlabel('Sample No.')
		plt.ylabel('Error (Target Alt - Current Alt)')
		while self._closePlot == False:
			if self._plotData == True:
				Y = self.pidctrl.getErrorAccum()
				X = self.pidctrl.getxAxis()
				xMax = len(self.pidctrl.getErrorAccum())
				#plt.axis([xMin, xMax, yMin, yMax])
				#graph2[0].set_ydata(Y)
				#graph2[0].set_xdata(X)
				ax1.set_xlim(xMin, xMax)
				ax1.set_ylim(yMin, yMax)
				ax1.figure.canvas.draw()
				while len(X) != len(Y):
				    Y.append(self.pidctrl.getLastError())
				graph1.set_data(X,Y)

				while self.calculate == False:
				    d = 4
				thrustArray = self.thrustArray
				ax2.set_xlim(xMin, xMax)
				ax2.set_ylim(0, 60000)
				ax2.figure.canvas.draw()

				while len(X) != len(thrustArray):
				    thrustArray.append(self.current_thrust)

				graph2.set_data(X,thrustArray)

				# graph2[1].set_ydata(Y)
				# graph2[1].set_xdata(thrustArray)

				plt.draw()
				plt.pause(0.001)