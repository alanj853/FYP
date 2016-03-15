from PID import PID

class PIDController:

	errorAccum = [0]
	xAxis = [0]
	Kp = 5;
	Ki = 1;
	Kd = 1;
	maxError = 0
	minError = 0
	maxIncr = 2500
	count = 0
	errorThreshold = 0.25
	lastError = 0

	def __init__(self):
		# self.Kp = kp
		# self.Ki = ki
		# self.Kd = kd
		# self.maxIncr = maxIncr
		# self.errorThreshold = errorThreshold
		print "PID Controller Created"

	def determineIncrement(self, targetAlt, currentAlt):
		error = targetAlt - currentAlt;
		self.lastError = error
		if abs(error) < self.errorThreshold:
			error = 0
		self.errorAccum.append(error)
		self.count = self.count + 1 
		self.xAxis.append(self.count)
		self.maxError = max(self.errorAccum)
		self.minError = min(self.errorAccum)
		P = self._determineProportional(error)
		I = self._determineIntegral(self.errorAccum)
		D = self._determineDerivative(self.errorAccum)
		print "For Error = ", error ,", P = ", P, " I = ", I, " D = ", D
		inc = P + I + D
		if inc > self.maxIncr:
			inc = self.maxIncr
		if inc < -self.maxIncr:
			inc = -self.maxIncr
		return inc
		#return 100

	
	def getLastError(self):
		return self.lastError

	def _determineProportional(self, error):
		P = self.Kp*error
		return P;

	def _determineIntegral(self, errorAccum):
		return self.Ki*sum(errorAccum);
		

	def _determineDerivative(self, errorAccum):
		l = len(errorAccum)
		currentError = errorAccum[l-1]
		previousError = errorAccum[l-2]
		D = self.Kd*(currentError - previousError)
		return D; ## will return current slope

	def getErrorAccum(self):
		return self.errorAccum;

	def getxAxis(self):
		return self.xAxis;

	def getMaxError(self):
		return self.maxError

	def getMinError(self):
		return self.minError

	def setPGain(self, x):
		self.Kp = x

	def setIGain(self, x):
		self.Ki = x

	def setDGain(self, x):
		self.Kd = x
