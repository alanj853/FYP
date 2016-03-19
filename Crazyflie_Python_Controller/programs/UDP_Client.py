import socket

import os
import sys

class UDP_Client:
	PORT  = 0
	IP = ""
	sock = ""
	MESSAGE = "CF:Client-Request_Coordinates"

	def __init__(self, ip, port):
		self.PORT = port
		self.IP = ip
		print "UDP Client object created at add: ", ip, " on port: ", port

	def requestData(self):
		# assign class variables to local variables. It makes code cleaner as we don't have to type "self" all of the time
		# I have commmented out print statements here. You can uncomment them for debugging purposes but it will make overall output messy
		MESSAGE = self.MESSAGE
		IP = self.IP
		PORT = self.PORT
		sock = self.sock 

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
		sock.connect((IP, PORT)) ## connect to port and host
		sock.sendto(MESSAGE,(IP, PORT)) ## send message to request data from server
		#print "Sent Request. Awaiting Reply"
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		#print "Got Reply"
		print data
		return data

	def getPort(self):
		return self.PORT

	def getIP(self):
		return self.IP

	def setPort(self, port):
		self.PORT = port

	def setIP(self, ip):
		self.IP = ip
