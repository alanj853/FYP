

class SubPlot():
	title = ""
	X = []
	Y = []
	XMin = 0
	XMax = 0
	YMin = 0
	YMax = 0
	YLabel = ""
	XLabel = ""

	def __init__(self, title):
		self.title = title
		print "Subplot object created: '", title ,"'"

	def _printPlotDetails(self):
		print "Title: ", self.title
		print "XLabel: ", self.XLabel
		print "YLabel: ", self.YLabel
		print "X Data: ", self.X
		print "Y Data: ", self.Y
		print "X range: ", self.XMin , " - ", self.XMax
		print "Y range: ", self.YMin , " - ", self.YMax

