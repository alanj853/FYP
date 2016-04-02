
"""
Simple program that allows user to control motors from the keyboard of their machine
IS WORKING

ONLY OPEN IN SUBLIME TEXT as other programs might fuck up the format
"""

import os
import sys
from threading import Thread
import time, math
from datetime import datetime, date

#FIXME: Has to be launched from within the example folder
sys.path.append("../lib")
sys.path.append("C:\Users\Alan\Dropbox\crazyflie-clients-python\lib")
sys.path.append("C:\Python27\Lib\site-packages")
import cflib
from cflib.crazyflie import Crazyflie

import cflib.crtp
from cflib.crazyflie import Crazyflie

from PIDController import PIDController
from Logger import Logger
from Plotter import Plotter
from UDP_Client import UDP_Client


class FlightController:

    # init function to connect to crazyflie
    def __init__(self, link_uri):
        #Initialize and run the example with the specified link_uri """
        self.is_connected = True
        self._cf = Crazyflie()
        self.plotOn = True
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print "Connecting to %s" % link_uri

        # initial logger, UDP client and PLotter
        self._logger = Logger(self._cf)
        self._udpClient = UDP_Client("127.0.0.1", 5000)
        
        self.pidctrlr_alt = PIDController("Alt controller")
        self.pidctrlr_x = PIDController("Gyro.x controller")
        self.pidctrlr_y = PIDController("Gyro.y controller")

        self.pidctrlr_t = PIDController("Thrust controller")
        self.pidctrlr_r = PIDController("Roll controller")

        # add variables to log
        self._logger.logNewVar("baro.asl", "float")
        self._logger.logNewVar("gyro.x", "float")
        self._logger.logNewVar("gyro.y", "float")

        self.pidctrlr_alt.setPGain(0)
        self.pidctrlr_alt.setIGain(0)
        self.pidctrlr_alt.setDGain(.01)

        self.pidctrlr_x.setPGain(5)
        self.pidctrlr_x.setIGain(1)
        self.pidctrlr_x.setDGain(1)

        self.pidctrlr_y.setPGain(5)
        self.pidctrlr_y.setIGain(1)
        self.pidctrlr_y.setDGain(1)

        self.pidctrlr_t.setPGain(.25) ## .25 works (sort of) with i = 0, d = 0
        self.pidctrlr_t.setIGain(.0005) ## try 0006,0007, ... etc tomorrow
        self.pidctrlr_t.setDGain(.000)
        self.pidctrlr_t.setErrorThreshold(30)

        self.pidctrlr_r.setPGain(.1)
        self.pidctrlr_r.setIGain(.1)
        self.pidctrlr_r.setDGain(.1)
        self.pidctrlr_r.setMaxError(1)

        self.plotter1 = Plotter("Plot 1", self.plotOn)

        self.best_matrix = "Not Assigned" ## the sub frame with the most free space -- see documentation
        self.turn_off_UDP_client = False;
        self._motors_on = True; ## variable for motors on
        self.windows_linux = "linux" ## type of machine client is running on
        self.curr_alt = 45;
        self.start_time = 0
        self.current_thrust = 0
        self.current_roll = 0
        self.current_pitch = 0
        self.altHold = False



    ## this method is called when a successful connection to the CF has been made
    def _connected(self, link_uri):

        Thread(target=self._motor_controller).start() # start the thread for controlling the motors
        #Thread(target=self._logger._begin_logging).start()
        Thread(target=self._udpClient.run).start()

        #Thread(target=self.plotter1.plot).start()

        
        print "Connected to ", link_uri
    

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print "Connection to %s failed: %s" % (link_uri, msg)
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print "Connection to %s lost: %s" % (link_uri, msg)

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print "Disconnected from %s" % link_uri
        self.is_connected = False


    

    def getAverage(self):
        thrustCompensation = .04
        altList = []
        s_time = time.time()
        f_time = s_time + .1
        curr_time = time.time()
        while(curr_time < f_time):
            altList.append(self.curr_alt)
            curr_time = time.time()
        averageAlt = sum(altList)/len(altList)


        print "Return alt = ", averageAlt
        return averageAlt


    def calNewThrust(self, targetAlt, targetX, targetY):
        currAlt = self._logger.retrieveVar("baro.asl")
        currX = self._logger.retrieveVar("gyro.x")
        currY = self._logger.retrieveVar("gyro.y")

        # print "currAlt = ", currAlt
        # print "currXaccel = ", currXaccel
        # print "currYaccel = ", currYaccel

        thrustFactor1 = self.pidctrlr_alt._determineIncrement(targetAlt, currAlt)
        t = self.pidctrlr_alt.getErrorAccum()

        thrustFactor2 = self.pidctrlr_x._determineIncrement(targetX, currX)
        x = self.pidctrlr_x.getErrorAccum()

        thrustFactor3 = self.pidctrlr_y._determineIncrement(targetY, currY)
        y = self.pidctrlr_y.getErrorAccum()

        self.plotter1.update(t, x, y)

        thrust = self.current_thrust
        roll = self.current_roll
        pitch = self.current_pitch

        thrust = thrust + thrustFactor1 
        roll = roll + thrustFactor2
        pitch = pitch + thrustFactor3
        
        print "thrust is now: ", thrust, " Roll is now: ", roll, " Pitch is now: ", pitch

        factorList = []
        factorList.append(thrust)
        factorList.append(roll)
        factorList.append(pitch)

        return factorList


    def _turnOffAllProcesses(self):
        self._udpClient.disconnectClient()

    def _detectObject(self):
        x = (self._udpClient.getXerr())
        x = float(float(x)/1000);
        y = self._udpClient.getYerr()

        thrustFactor = self.pidctrlr_t._determineIncrement(239, y)
        rollFactor = 0#self.pidctrlr_r._determineIncrement(319, x)

        self.current_thrust = self.current_thrust + thrustFactor
        self.current_roll = self.current_roll + rollFactor
        print "Thrust = ", self.current_thrust, " roll = ",self.current_roll, " x = ", rollFactor, " y = ", thrustFactor
        return 1;
  
        
    # auto pilot function
    def _auto_pilot(self, curr_thrust, curr_roll, curr_pitch):
        char = self._getch(); # get the character that was pressed by the user
        thrust = curr_thrust;
        roll = curr_roll;
        pitch = curr_pitch;

        while char != "j" and char != "o":

            if self.best_matrix == '0':
                pitch = pitch - .5 # reverse if not clear space
                print "reverse"
            elif self.best_matrix == '1':
                thrust = thrust + 50
                roll = roll - .5
                print "Increase Thrust and Roll Left"
            elif self.best_matrix == '2':
                thrust = thrust + 50
                print "Increase Thrust"
            elif self.best_matrix == '3':
                thrust = thrust + 50
                roll = roll + .5
                print "Increase Thrust and Roll Right"
            elif self.best_matrix == '4':
                roll = roll - .5
                print "Roll Left"
            elif self.best_matrix == '6':
                roll = roll + .5
                print "Roll Right"
            elif self.best_matrix == '7':
                thrust = thrust - 50
                roll = roll - .5
                print "Decrease Thrust and Roll Left"
            elif self.best_matrix == '8':
                thrust = thrust - 50
                print "Decrease Thrust"
            elif self.best_matrix == '9':
                thrust = thrust - 50
                roll = roll + .5
                print "Decrease Thrust and Roll Right"
            ## Still maintain manual Yaw Control (for now)     
            elif char == "a":
                print "turning left"
                self._set_movement(roll, pitch, -50, thrust)
                time.sleep(.25)
                self._set_movement(roll, pitch, 0, thrust)
            elif char == "d":
                print "turning right"
                self._set_movement(roll, pitch, 50, thrust)
                time.sleep(.25)
                self._set_movement(roll, pitch, 0, thrust)
            else:
                print "maintain thrust and roll" #self.best_matrix == 5, where we just maintain current position


            self._set_movement(roll, pitch, 0, thrust); ## set the new parameters
            print "Thrust = ", thrust, " Roll = ",roll, " pitch = ", pitch
            time.sleep(.1)
            char = self._getch();
        print "Done AutoPilot"


    # function to set thrust, roll, pitch and yaw parameters on crazyflie    
    def _set_movement(self,roll, pitch, yaw, thrust):
        if self._motors_on == True:
            if thrust > 60000:
                print "Cannot set thrust greater than 60000."
                thrust = 60000
            elif thrust < 15000:
                print "Cannot set thrust lower than 15000."
                thrust = 15000
            else:
                thrust = thrust
            self._cf.commander.send_setpoint(roll, pitch, yaw, thrust)


        
    def _motor_controller(self):
        self._print_controls()
        self.start_time = time.time()
        self.current_roll = 0
        self.current_pitch = 0
        self.current_thrust = 15000
        targetAlt = 0
        targetX = 0
        targetY = 0
        altHold = False
        char = ""

        while 1:
            
            self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
            
            char = self._getch()
            self.altHold = altHold
            if char == "h":
                print "hover ON"
                #self._cf.param.set_value('flightmode.althold', "True")
                #self._auto_pilot(self.current_thrust, self.current_roll, self.current_pitch)
                altHold = True
                targetAlt = 0#self._logger.retrieveVar("baro.asl")
                targetX = 0#self._logger.retrieveVar("gyro.x")
                targetY = 0#self._logger.retrieveVar("gyro.y")
                self.pidctrlr_t.reset()
                print "Target Alt: ", targetAlt
                
            if char == "p":
                if self._motors_on == True:
                    self._motors_on = False
                    print "Motors Now off"
                elif self._motors_on == False:
                    self._motors_on = True
                    print "Motors Now on"

            if altHold == True:
				x = self._detectObject()
				#arr = self.calNewThrust(targetAlt, targetX, targetY)
                #self.current_thrust = arr[0]
                #self.current_roll = arr[1]
                #self.current_pitch = arr[2]
				#



            if char == "j":
                print "hover OFF"
                self._cf.param.set_value('flightmode.althold', "False")
                altHold = False

	        ## Emergency Brake! Turns all motors off immediately. No soft landing
            if char == "o":
               self._set_movement(0, 0, 0, 0)
               print "All Motors OFF NOW"
               break

	        ## Thrust Control
            if char == "q" and altHold == False:
                self.current_thrust = 44000
                print "Take-off thrust. Thrust = ", self.current_thrust
            if char == "w" and altHold == False:
                self.current_thrust = self.current_thrust + 50
                print "Increasing thrust. Thrust = ", self.current_thrust
            if char == "s" and altHold == False:
                self.current_thrust = self.current_thrust - 50
                print "Descreasing thrust. Thrust = ", self.current_thrust


	        ## For Big Thrust Increments/Decrements
            if char == "t" and altHold == False:
                self.current_thrust = self.current_thrust + 500
                print "Increasing thrust. Thrust = ", self.current_thrust
            if char == "g" and altHold == False:
                self.current_thrust = self.current_thrust - 500
                print "Descreasing thrust. Thrust = ", self.current_thrust
            if char == "b" and altHold == False:
                self.current_thrust = self.current_thrust + 5000
                print "Boost of 5000. Thrust = ", self.current_thrust
            if char == "n" and altHold == False:
                self.current_thrust = self.current_thrust - 5000
                print "DeBoost of 5000. Thrust = ", self.current_thrust

            ## Roll control
            if char == "\x1b[C" or char == "M": ## this is the right arrow on the keyboard translation
                print "moving right "
                #if altHold == False:
                self._set_movement(15, self.current_pitch, 0, self.current_thrust)
                time.sleep(.25)
                self.current_roll += .5
                print "     roll changed to: ", self.current_roll
                self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
            if char == "\x1b[D" or char == "K":
                print "moving left "
                #if altHold == False:
                self._set_movement(-15, self.current_pitch, 0, self.current_thrust)
                time.sleep(.25)
                self.current_roll -= .5
                print "     roll changed to: ", self.current_roll
                self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)

            ## Pitch Control
            if char == "\x1b[B" or char == "P":
                print "moving backwards "
                #if altHold == False:
                self._set_movement(self.current_roll, -15, 0, self.current_thrust)
                time.sleep(.25)
                self.current_pitch -= .5
                print "     pitch changed to: ", self.current_pitch
                self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
            if char == "\x1b[A" or char == "H":
                print "moving forwards "
                #if altHold == False:
                self._set_movement(self.current_roll, 15, 0, self.current_thrust)
                time.sleep(.25)
                self.current_pitch += .5
                print "     pitch changed to: ", self.current_pitch
                self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)

    	    ## Yaw Control	    
    	    if char == "a":
                print "turning left"
                self._set_movement(self.current_roll, self.current_pitch, -50, self.current_thrust)
                time.sleep(.25)
                self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
    	    if char == "d":
        		print "turning right"
        		self._set_movement(self.current_roll, self.current_pitch, 50, self.current_thrust)
                        time.sleep(.25)
        		self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
	    
	        ## Landing
            if char == "l":
                print "pressed l ==> landing..."
                l_char = self._getch()
                while self.current_thrust >= 15000 and l_char != "\n":
                    self.current_thrust = self.current_thrust - 750
                    print "     current thrust = ", self.current_thrust
                    self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
                    l_char = self._getch()
                    time.sleep(.5)
                #break
	   
            ## Enter. Press "Enter" when cf has been calibrated
            if char == "\n":
                print "Calibration Done"
                break


        self._turnOffAllProcesses()
        self._cf.close_link()
    
    
    
    def _print_controls(self):
        print "======================================="
        print "===============CONTROLS================"
        print "======================================="
        print "***************Thrust***************"
        print "		     Take-off: q"
        print "		High Increase: t"
        print "		 Low Increase: w"
        print "		High Increase: g"
        print "		 Low Decrease: s"
        print "***************Pitch***************"
        print "		      Forward: up-arrow"
        print "		    Backwards: down-arrow"
        print "***************Roll***************"
        print "			 Left: left-arrow"
        print "			Right: right-arrow"
        print "***************YAW***************"
        print "			 Left: a"
        print "			Right: d"
        print "***************HOVER***************"
        print "		     Hover ON: h"
        print "		    Hover OFF: j"
        print "***************LAND***************"
        print "		         Land: l"
        print "***************EMERGENCY STOP***************"
        print "		   Motors OFF: o"
        print "======================================="
        print "======================================="
        print "======================================="


    # method to capture the character the user has pressed
    # it has 2 versions however, one for windows machine and one for linux
    # this is because they both require separate libraries to perform this task    
    def _getch(self):
        if self.windows_linux == "linux":
            try:
                import fcntl
                import termios
            except ImportError:
                print "You are running on a windows machine"
                print "Please put 'windows' as the first argument when running this program."
                self._set_movement(0, 0, 0, 0)
                print "All Motors OFF NOW"
                self._cf.close_link()
                sys.exit()
            fd = sys.stdin.fileno()

            oldterm = termios.tcgetattr(fd)
            newattr = termios.tcgetattr(fd)
            newattr[3] = newattr[3] & ~ termios.ICANON & ~ termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, newattr)

            oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
            c = ""
            try:
                curr = time.time()
                target = curr + .1
                while curr < target:
                    try:
                        c = sys.stdin.read(3)
                        print "pressed ", repr(c)
                    except IOError: pass
                    curr = time.time()
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
                fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
                return c;
        else:
            import msvcrt
            curr = time.time()
            target = curr + .1
            c = ""
            while curr < target:
                if msvcrt.kbhit():
                    c = msvcrt.getch();
                curr = time.time()
            if c != "":
                print "This is pressed ", c
            return c;
    
if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print "Scanning interfaces for Crazyflies..."
    available = cflib.crtp.scan_interfaces()
    print "Crazyflies found:"
    for i in available:
        print i[0]

    if len(available) > 0:
        le = FlightController("radio://0/80/250K")
        try:
            if sys.argv[1] != "":
                if sys.argv[1] == "windows":
                    le.windows_linux = sys.argv[1];
                    print "Using windows configuration"
                else:
                    print "Using linux configuration"
        except IndexError: 
            print "Using linux configuration"
        try:
            if sys.argv[2] != "":        
                if sys.argv[2] == "off":
                    le._motors_on = False
                    print "Motors are disabled"
                else:
                    print "Motors are enabled"
        except IndexError: 
            print "Motors are enabled"
        while le.is_connected:
            time.sleep(1)
        print "Done"
        stop_time = time.time()
        print "Total Flight Time: ", int(stop_time - le.start_time), " seconds"
        ts = time.time()
        dt = datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        # Open a file to write flight details to
        fo = open("flight_details.txt", "a")
        if le._motors_on == False:
            msg = str(dt + ": " + "Total Flight Time: " + str(int(stop_time - le.start_time)) + " seconds MOTORS OFF\n")
        else:
            msg = str(dt + ": " + "Total Flight Time: " + str(int(stop_time - le.start_time)) + " seconds\n")
        fo.write(msg);

        # Close opened file
        fo.close()
        le.turn_off_UDP_client = True;
        le.plotter1.updateY(le.pidctrlr_t.getErrorAccum(),le.pidctrlr_t.getIncAccum(),0)
        #le.plotter1.updateX(le.pidctrlr_t.getXAxis())
        le.plotter1.plot()
        print "Time under AutoPilot = ", le.pidctrlr_t.getControlTime(), " seconds"
        #le.pidctrlr_t.getXAxis()
    else:
        print "No Crazyflies found, cannot run example"
