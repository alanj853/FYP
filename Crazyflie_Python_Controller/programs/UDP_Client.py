""" 
Class to create a UDP client for talking to server. It is hardcoded to make 
4 requests to the server for data. the requests are for 
	1. best matrix
	2. X coordinate of tracked object
	3. Y coordinate of tracked object
	4. Area of tracked object


"""import socket

import os
import sys

class UDP_Client:
	
	def __init__(self, ip, port):
		self.PORT = port
		self.IP = ip
		print "UDP Client object created at add: ", ip, " on port: ", port
		self.sock = ""
		self.MESSAGE1 = "CF:Client-Request_DetectWhiteSpace"
		self.MESSAGE2 = "CF:Client-Request_DetectObject_Xcoordinate"
		self.MESSAGE3 = "CF:Client-Request_DetectObject_Ycoordinate"
		self.MESSAGE4 = "CF:Client-Request_DetectObject_ObjectArea"
		self.bestMatrix = "no data"
		self.Ycoordinate = 0
		self.Xcoordinate = 0
		self.ObjectArea = 0
		self.runClient = True

	def run(self):
		while(self.runClient == True):
			# assign class variables to local variables. It makes code cleaner as we don't have to type "self" all of the time
			# I have commmented out print statements here. You can uncomment them for debugging purposes but it will make overall output messy

			## request 1
			MESSAGE = self.MESSAGE1
			IP = self.IP
			PORT = self.PORT

			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
			self.sock.connect((IP, PORT)) ## connect to port and host
			self.sock.sendto(MESSAGE,(IP, PORT)) ## send message to request data from server
			#print "Sent Request. Awaiting Reply"
			self.data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
			self.bestMatrix = self.data
			#print "Got Reply"
			#print self.data
			
			## request 2
			MESSAGE = self.MESSAGE2
			IP = self.IP
			PORT = self.PORT

			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
			self.sock.connect((IP, PORT)) ## connect to port and host
			self.sock.sendto(MESSAGE,(IP, PORT)) ## send message to request data from server
			#print "Sent Request. Awaiting Reply"
			data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
			self.Xcoordinate = int(data)
			#print "Got Reply"
			#print self.data
			

			## request 3
			MESSAGE = self.MESSAGE3
			IP = self.IP
			PORT = self.PORT

			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
			self.sock.connect((IP, PORT)) ## connect to port and host
			self.sock.sendto(MESSAGE,(IP, PORT)) ## send message to request data from server
			#print "Sent Request. Awaiting Reply"
			data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
			self.Ycoordinate = int(data)
			#print "Got Reply"
			#print self.data


			## request 4
			MESSAGE = self.MESSAGE4
			IP = self.IP
			PORT = self.PORT

			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
			self.sock.connect((IP, PORT)) ## connect to port and host
			self.sock.sendto(MESSAGE,(IP, PORT)) ## send message to request data from server
			#print "Sent Request. Awaiting Reply"
			data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
			self.ObjectArea = float(data)
			#print "Got Reply"
			#print self.data

		self.sock.close()
		print "Client Closed"

	def requestData(self):
		return self.data		

	def disconnectClient(self):
		self.runClient = False
		

	def getPort(self):
		return self.PORT

	def getIP(self):
		return self.IP

	def setPort(self, port):
		self.PORT = port

	def setIP(self, ip):
		self.IP = ip
		
	def getXcoordinate(self):
		return self.Xcoordinate
		
	def getYcoordinate(self):
		return self.Ycoordinate

	def getObjectArea(self):
		return self.ObjectArea

	def getBestMatrix(self):
		return self.bestMatrix
