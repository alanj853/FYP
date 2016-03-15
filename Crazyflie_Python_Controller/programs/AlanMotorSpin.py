"""
Program for quadcopter to take off, hold, turn and land 
"""
# -----------------------------------------------------------------------

""" Importing required libraries """
import sys,socket,select
import time
from threading import Thread

sys.path.append("../lib")
import re
import cflib
import cfclient
from cflib.crazyflie import Crazyflie
from cfclient.utils.logconfigreader import LogConfig
import cflib.crtp
import logging
logging.basicConfig(level=logging.ERROR)

#use whichever port and packet size you used on the C side



"""
port = 12346
packetSize = 1000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", port)) #changed to "localhost"; was ""
    

port =  65444
destination = "localhost"
s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s1.bind(("", port)) #changed to "port"; from sport ""
"""
#------------------------------------------------------------------------
#NEW ATTEMPT AT Tx/Rx Python-Python AFTER HELLO WORLD
 
UDP_IP = "127.0.0.1" #Define IP Addr
UDP_PORT_TX = 32567 #Define Tx(C++) Port
UDP_PORT_RX = 23758 #Define Rx(Python[This Program!]) Port


#Initialise Socket 
sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT_RX)) #Bind Socket to IP addr and (Rx)Port number above^^
#Sockets Good To Go!


# -----------------------------------------------------------------------

class ProjectFlight:

# -----------------------------------------------------------------------
    
    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie() # Creating instance of Crazyflie

        """ Adding callbacks depending on connection status """
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
        

        # attempt to open radio link
        self._cf.open_link(link_uri)

        print "Connecting to %s" % link_uri
        
# ------------------------------------------------------------------------        

    def _connected(self, link_uri):
        """ This callback is called from the Crazyflie API when a Crazyflie
            has been connected and the TOCs have been downloaded."""


        print("Setting Up Logger...")
        
        # The definition of the logconfig can be made before connecting
        #self._lg_stab = LogConfig(name="baro", period_in_ms=10)
        #self._lg_stab.add_variable("baro.asl", "float")
        
        self._lg_stab = LogConfig(name="Logger", period_in_ms = 100)
        #self._lg_stab.add_variable("altHold.altTarget", "float")
        #self._lg_stab.add_variable("altHold.err", "float")
        #self._lg_stab.add_variable("gyro.x", "float")
        #self._lg_stab.add_variable("gyro.y", "float")
        #self._lg_stab.add_variable("gyro.z", "float")
        self._lg_stab.add_variable("baro.asl", "float")
        #self._lg_stab.add_variable("baro.aslRaw", "float")
        #self._lg_stab.add_variable("baro.aslLong", "float")

        print("Seems To Be OK...")
        
        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        self._cf.log.add_config(self._lg_stab)
        if self._lg_stab.valid:
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
            print("Now something should really be happening...")
        else:
            print("Could not add logconfig since some variables are not in TOC")

        # Start a separate thread to do the quadcopter flight testing
        print("Connected!")
        Thread(target=self._start_flight).start()

    def _connection_failed(self, link_uri, msg):
        """ Callback when connection initial connection fails (ie. no Crazyflie
            at the specified address) """
        print "Connection to %s failed: %s" % (link_uri, msg)

    def _connection_lost(self, link_uri, msg):
        """ Callback when disconnected after a connection has been made (ie.
            Crazyflie moves out of range) """
        print "Connection to %s lost: %s" % (link_uri, msg)
        sock.close()
        print "socket closed"

    def _disconnected(self, link_uri):
        """ Callback when the Crazyflie is disconnected (called in all cases) """
        print "Disconnected from %s" % link_uri

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print "Error when logging %s: %s" % (logconf.name, msg)

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        print "[%d][%s]: %s" % (timestamp, logconf.name, data)



# --------------------------------------------------------------------------------

    """ Function where test flight takes place """
    def _start_flight(self):
        while 1:

            ########################
			
            #Set thrust to 10000 (not very high) and everything else to 0
            thrust = 15000
            pitch = 0
            roll = 0
            yawrate = 0
            hover = 0

		    #Repeat 20 times...
            for x in range(0, 20):
				#Send above values to Crazyflie
                                #self._cf.commander.send_setpoint(roll, pitch,yawrate,thrust, hover)
                self._cf.commander.send_setpoint(roll, pitch,yawrate,thrust)
				#Sleep for .1 seconds
                time.sleep(0.1)

			#Close up socket and Crazyflie link then exit program (i think...)
            self._cf.commander.hello_world("This is my message")
            sock.close()
            print "socket closed"
            print "stopped logging"
            self._cf.close_link()
            print "link closed"
            print "exiting"
            sys.exit()
            
            ########################
			
            
            """data received from computer"""
            #data, address = sock.recvfrom(int(packetSize))
            print"ready..."
            
            ACK = "a"
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

            print "received message:", data
            print "sender port:", addr

            sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))
    
            print "sent"
            
            """ Sequential Sequence of functions called """
            if data == 't':
                self._takeoff()
                continue
            if data[0] == 'h':
                self._hold()
                continue
            if data[0] == 's':
                self._stop()
                continue
            if data[0] == 'B':
                self._leftback()
                continue
            if data[0] == 'C':
                self._rightup()
                continue
            if data[0] == 'D':
                self._rightback()
                continue
            if data[0] == 'l':
                self._land()
                continue
            
# -------------------------------------------------------------------------------------
    
    """ Function for quadcopter to take off """
    def _takeoff(self):
        
        """ Setting flight control values, pitch and roll set to compensate for drift """
        thrust = 0
        pitch = -8
        roll = 35
        yawrate = 0
        hover = 0
        
        print "Taking off"
        
        """ Send setpoint command using above variables, apply for 2 seconds """
        for x in range(0, 20):
            self._cf.commander.send_setpoint(roll, pitch,yawrate,thrust, hover)
            time.sleep(0.1)
        
        thrust = 45000
        
        """ Allow quadcopter to settle at desired altitude for 2 extra seconds """
        for x in range(0, 2):
            self._cf.commander.send_setpoint(roll, pitch,yawrate,thrust, hover)
            time.sleep(0.1)
            print "Lifting off"
                
        #Inform Master Program that take off successful & entering hover mode
        sock.sendto("g", (UDP_IP, UDP_PORT_TX))
        
            
        self._hold()
        """sending data h to the visual studio to hold the helicopter"""
        """s1.sendto('h', (destination, sport))"""
# -------------------------------------------------------------------------------------
    
    """ Function for quadcopter to hold"""
    def _hold(self): 
        data = [1024]
        """ Setting flight control values, pitch and roll set to compensate for drift """
        pitch = -10
        roll = 20
        yawrate = 0
        hover = 1
        thrust = 32767

        i = 0
        print "Holding"
        """ Allow quadcopter to settle at desired altitude for 2 extra seconds """
        """for x in range(0, 20):
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)
            time.sleep(0.1)"""

        while 1:
            print "looping"
            i += 1
            
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)

            sock.setblocking(0)

            ready = select.select([sock], [], [], 0.0005)
            
            if ready[0]:
                print"ready..."
                
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                print "received message:", data
                print "sender port:", addr

                ACK = "a"
                sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))
                print "sent"
            """data received from computer"""
            #data, address = sock.recvfrom(int(packetSize))
            #print"ready..."
            
            #data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

            #print "received message:", data
            #print "sender port:", addr

            #sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))
    
            
            
            """ Sequential Sequence of functions called """
            if data[0] == 't':
                self._takeoff()
                continue
            if data[0] == 'h':
                self._hold()
                continue
            if data[0] == 's':
                self._stop()
                continue
            if data[0] == 'f':
                self._forward()###########
                continue
            if data[0] == 'R':
                self._turnRight()
                continue
            if data[0] == 'D':
                self._rightback()
                continue
            if data[0] == 'l':
                self._land()
                continue

            time.sleep(0.1)
            if i == 100:
                break
                


            
        """c means continue holding, continue holding"""
        """s1.sendto('h', (destination, sport))"""
# --------------------------------------------------------------------------------
    
    """ Function for quadcopter to roll left and pitch up"""
    def _stop(self):
        
            
        """ Setting flight control values, pitch and roll set to compensate for drift """
        pitch = -10
        roll = 23
        yawrate = 0
        hover = 1
        thrust = 32767
        
        print "Stopping"
        for x in range(0, 1):
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)
            time.sleep(0.1)

        self._hold()

# --------------------------------------------------------------------------------
    
    """ Function for quadcopter to roll left and pitch back"""
    def _forward(self):

        data = [1024]
            
        """ Setting flight control values, pitch and roll set to compensate for drift """
        pitch = -4
        roll = 18
        yawrate = 0
        hover = 1
        thrust = 32767
        
        print "Moving forward"
        for x in range(0, 1):
            self._cf.commander.send_setpoint(roll, pitch,yawrate, thrust, hover)
            time.sleep(0.1)

        while 1:
            print "looping"
            #self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)

            sock.setblocking(0)

            ready = select.select([sock], [], [], 0.0005)
            
            if ready[0]:
                print"ready..."
                
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                print "received message:", data
                print "sender port:", addr

                ACK = "a"
                sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))
                print "sent"
            """data received from computer"""
            #data, address = sock.recvfrom(int(packetSize))
            #print"ready..."
            
            #data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

            #print "received message:", data
            #print "sender port:", addr

            #sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))
    
            
            
            """ Sequential Sequence of functions called """
            if data == 't':
                self._takeoff()
                continue
            if data[0] == 'h':
                self._hold()
                continue
            if data[0] == 's':
                self._stop()
                continue
            if data[0] == 'f':
                self._forward()
                continue
            if data[0] == 'C':
                self._rightup()
                continue
            if data[0] == 'D':
                self._rightback()
                continue
            if data[0] == 'l':
                self._land()
                continue

# --------------------------------------------------------------------------------
    
    """ Function for quadcopter to turn right pitch up"""
    def _turnRight(self):
        
            
        """ Setting flight control values, pitch and roll set to compensate for drift """
        pitch = -10
        roll = 20
        yawrate = 90
        hover = 1
        thrust = 32767
        
        print "Yaw Right.. Hopefully! or maybe left we'll see..."
        for x in range(0, 10):
            self._cf.commander.send_setpoint(roll, pitch, yawrate,thrust, hover)
            time.sleep(0.1)

        self._hold()
        
# --------------------------------------------------------------------------------
    
    """ Function for quadcopter to turn right and then pitch back"""
    def _rightback(self):
        
            
        """ Setting flight control values, pitch and roll set to compensate for drift """
        thrust = 34000
        yawrate = 0
        hover = 1
        roll = 16
        pitch = 1.8
        
        print "Roll right"
        for x in range(0, 1):
            self._cf.commander.send_setpoint(roll, pitch, yawrate,thrust, hover)
            time.sleep(0.1)
        roll = 1.5
        pitch = -15
        print "Pitch back"
        for x in range(0, 1):
            self._cf.commander.send_setpoint(roll, pitch, yawrate,thrust, hover)
            time.sleep(0.1)

# ------------------------------------------------------------------------------    
    
    """ Function to land quadcopter """
    def _land (self):

        
        """ Setting flight control values, pitch and roll set to compensate for drift """
        thrust = 40000  # disabling thrust
        pitch = 0
        roll = 15
        yawrate = 0
        hover = 0 # disabling hover mode
        
        print "Landing"
        
        """ Allow quadcopter to drop for 200ms """
        self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)
        time.sleep(.15)

        thrust = 30000  # disabling thrust

        self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)
        time.sleep(.15)
        
        #""" Activate thrust just before hitting ground to cushion landing """
        #thrust = 15000
        #self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust, hover)
        #time.sleep(1.1)
        self._lg_stab.stop()
        print "stopped logging"
        sock.close()
        print "socket closed"
        print "stopped logging"
        self._cf.close_link()
        print "link closed"
        print "exiting"
        sys.exit()
            
# -------------------------------------------------------------------------------

""" Activate program if called from command line """

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    """
    #data, address = s.recvfrom(int(packetSize))
    #print "recieved " + data

    #time.sleep(2)
    print "sending..."
    s1.sendto('h', (destination, port)) #removed s from port
    
    print "sent?..."
    """
#Attempt at better Socket actions iin main:


    #while True:
    """ 
        while True:
            print"ready..."
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

            print "received message:", data
            print "sender port:", addr
            break

        print "break"

        #ACK = "thanks!"
        ACK = "a"
        #time.sleep(5)

        sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))


        print "sent"
        #sock.close()
        print "NOT closed"

        while True:
            print"ready..."
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

            print "received message:", data
            print "sender port:", addr
            break

        print "break"

        #ACK = "thanks!"
        ACK = "a"
        #time.sleep(5)

        sock.sendto(ACK, (UDP_IP, UDP_PORT_TX))
        
        

        print "sent"
    #time.sleep(5)
    sock.close()
    print "closed"
    """
    
    # Scan for Crazyflies and use the first one found
    print "Scanning interfaces for Crazyflies..."
    available = cflib.crtp.scan_interfaces()
    print "Crazyflies found:"
    for i in available:
        print i[0]

    if len(available) > 0:
        le = ProjectFlight(available[0][0])
    else:
        print "No Crazyflies found, cannot run example"
