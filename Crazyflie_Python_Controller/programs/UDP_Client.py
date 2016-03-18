import socket

class UDP_Client:
	PORT  = 0
	IP = ""
	sock = ""
	MESSAGE = "CF:Client-Request_Coordinates"

	def __init__(self, port, ip):
		PORT = port
		IP = ip

	def requestData(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
        sock.connect((IP, PORT)) ## connect to port and host
        sock.sendto(MESSAGE,(IP, PORT)) ## send message to request data from server
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        return data

	def getPort(self):
		return PORT

	def getIP(self):
		return IP

	def setPort(self, port):
		PORT = port

	def setIP(self, ip):
		IP = ip
