

class PID:

	## private vars
	Kp = 0
	Ki = 0
	Kd = 0

	def __init__(self):
		print "Starting PID";

	def getGetOutput(self, currentThrust, currentAltitude):
		print ""

	def getKp(self):
		return self.Kp

	def getKi(self):
		return self.Ki

	def getKd(self):
		return self.Kd

	def setKp(self, newKp):
		self.Kp = newKp

	def setKi(self, newKi):
		self.Ki = newKi

	def setKd(self, newKd):
		self.Kd = newKd