
"""
This is the main program for the flight controller program. User can run this program
(provided they have the crazyflie requirements installed, See bitcraze github page for 
more info) by typing from this files directory into the terminal
	python main.py <arg1> <arg2>
where arg1 can be either "windows" or "linux" for whatever OS program is running on
where arg2 can be "off" to turn motors off on start up. If any other command is entered, motors will
spin upon connection

"""

import os
import sys
from threading import Thread
import time, math
from datetime import datetime, date

## these systems appends are specific to my personal machine
## User will need to configure their own. Just make sure they point to the craxyflie "lib"
## folder and also site packages
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
        self.pidctrlr_p = PIDController("Pitch controller")

        # add variables to log
        self._logger.logNewVar("baro.asl", "float")
        #self._logger.logNewVar("gyro.x", "float")
        #self._logger.logNewVar("gyro.y", "float")
        self._logger.logNewVar("pm.vbat", "float")

        self.pidctrlr_alt.setPGain(100) ## set gains and other paramters of controllers
        self.pidctrlr_alt.setIGain(0.00)# 032
        self.pidctrlr_alt.setDGain(320)
        self.pidctrlr_alt.setErrorThreshold(0.1)
        self.pidctrlr_alt.setMaxInc(2000)

        self.pidctrlr_x.setPGain(5)
        self.pidctrlr_x.setIGain(1)
        self.pidctrlr_x.setDGain(1)

        self.pidctrlr_y.setPGain(5)
        self.pidctrlr_y.setIGain(1)
        self.pidctrlr_y.setDGain(1)

        self.pidctrlr_t.setPGain(.5) ## .25 works (sort of) with i = 0, d = 0
        self.pidctrlr_t.setIGain(.005) ## try 0006,0007, ... etc tomorrow
        self.pidctrlr_t.setDGain(1.4)
        self.pidctrlr_t.setErrorThreshold(10)

        self.pidctrlr_r.setPGain(.0001)
        self.pidctrlr_r.setIGain(0)
        self.pidctrlr_r.setDGain(0)
        self.pidctrlr_r.setMaxInc(1)

        self.plotter1 = Plotter("Plot 1", self.plotOn)
        self.batteryReadings = []
        self.yPositionReadings = []
        self.baroReadings = []

        self.best_matrix = "Not Assigned" ## the sub frame with the most free space -- see documentation
        self.turn_off_UDP_client = False;
        self._motors_on = True; ## variable for motors on
        self.windows_linux = "linux" ## type of machine client is running on
        self.start_time = 0
        self.current_thrust = 0
        self.current_roll = 0
        self.current_pitch = 0
        self.altHold = False

        self._auto_pilot_mode = 1 ## change this value between 0,1 & 2 to enter various controllers 

        

        ## methods used for testing and writing data to files.
        ## has been hard coded for specific number of files operation
    def writeAllDataToTextFiles(self, vals1,vals2,vals3, vals4,vals5):
        fileName1 = open("Excel/error1.txt", "wb") ## create new file in folder called Excel (user will have to create folder first)
        fileName2 = open("Excel/Increments.txt", "wb")
        fileName3 = open("Excel/yPositionReadings.txt", "wb")
        fileName4 = open("Excel/batteryDrain1.txt", "wb")
        fileName5 = open("Excel/rollData.txt", "wb")

        for data in vals1:
            string = str(data) + ","
            fileName1.write(string)
        fileName1.close()

        for data in vals2:
            string = str(data) + ","
            fileName2.write(string)
        fileName2.close()

        for data in vals3:
            string = str(data) + ","
            fileName3.write(string)
        fileName3.close()

        for data in vals4:
            string = str(data) + ","
            fileName4.write(string)
        fileName4.close()

        for data in vals5:
            string = str(data) + ","
            fileName5.write(string)
        fileName5.close()
    


    ## this method is called when a successful connection to the CF has been made
    def _connected(self, link_uri):

        Thread(target=self._motor_controller).start() # start the thread for controlling the motors

        ## Depending on autopilot mode, different threads are started. This is because program will break its
        ## connection with the crazyflie if it runs too many threads. Read my thesis for more info on this
        if self._auto_pilot_mode != 1:
            Thread(target=self._logger._begin_logging).start()
        else:
            Thread(target=self._udpClient.run).start()

        
        print "Connected to ", link_uri
    

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print "Connection to %s failed: %s" % (link_uri, msg)
        self.is_connected = False
        #self._cf.close_link()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print "Connection to %s lost: %s" % (link_uri, msg)
        self._cf.close_link()

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print "Disconnected from %s" % link_uri
        self.is_connected = False
        #self._cf.close_link()


    
    ## function to turn off all processes running so program can end 
    def _turnOffAllProcesses(self):
        self._udpClient.disconnectClient()
        self.turnOffTest = True

    # auto pilot function
    def _auto_pilot(self, mode):
        # object avoidance using the area with the greatest amount of whitespace
        if mode == 0:
            best_matrix = self._udpClient.bestMatrix
            thrust = 0
            roll = 0
            pitch = 0
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
            else:
                print "maintain thrust and roll" #self.best_matrix == 5, where we just maintain current position

            self.current_thrust = thrust
            self.current_roll = roll
            self.current_pitch = pitch

        # altitude hold using object an image an reference point
        elif mode == 1:
            self.plotter1.ax3.set_title('Y Position')
            self.plotter1.ax5.set_title('Roll Error')
            x = (self._udpClient.getXcoordinate())
            x = float(float(x)/1000);
            y = self._udpClient.getYcoordinate()
            self.yPositionReadings.append(y)

            thrustFactor = self.pidctrlr_t._determineIncrement(239, y)
            rollFactor = 0#self.pidctrlr_r._determineIncrement(319, x)
            gravityFactor = 1#0.2297*2

            # batteryValue = self._logger.retrieveVar("pm.vbat")
            # self.batteryReadings.append(batteryValue)
            # if batteryValue < 4.2:
            #     batteryFactor = (batteryValue - 3.7)*100  ## attempt at adding battery factor to help as battery drained
            # else:
            #     batteryFactor = 0
            
            self.current_thrust = self.current_thrust + thrustFactor
            self.current_roll = self.current_roll - rollFactor
            print "Thrust = ", self.current_thrust, " roll = ",self.current_roll, " x = ", rollFactor, " y = ", thrustFactor

        # altitude hold using barometer readings
        elif mode == 2:
            self.plotter1.ax3.set_title('Barometer Reading')
            i = 0
            arrT = []
            currAlt = 0
            while i < 10:
                currAlt = self._logger.retrieveVar("baro.asl")
                arrT.append(currAlt)
                i = i + 1
            currAlt = sum(arrT)/len(arrT)
            self.baroReadings.append(currAlt)
            print "currAlt = ", currAlt

            thrustFactor = self.pidctrlr_alt._determineIncrement(self.targetAlt, currAlt)
            gravityFactor = 0.2297*2
            batteryValue = self._logger.retrieveVar("pm.vbat")
            self.batteryReadings.append(batteryValue)
            if batteryValue < 4.2:
                batteryFactor = (batteryValue - 3.7)*100
            else:
                batteryFactor = 0
            

            if thrustFactor < 0:
                thrustFactor = thrustFactor*gravityFactor

            self.current_thrust = self.current_thrust + thrustFactor + batteryFactor
            
            print "thrust is now: ", self.current_thrust, " Roll is now: ", self.current_roll, " Pitch is now: ", self.current_pitch

        elif mode == 3:
            area = self._udpClient.getObjectArea() 
            MAX_AREA_SIZE = 48000 ## area at which we want to start avoiding object 
            MAX_PITCH = self.current_pitch + 1
            ## TODO 
            """
            here is where the demo would go, if I had gotten that far.

            while True
                if  area < MAX_AREA_SIZE and self.current_pitch <= MAX_PITCH:
                    self.current_pitch = self.current_pitch + .1 ## move forwards (slowly)
                elif area >= MAX_AREA_SIZE:
                    self.current_thrust = self.current_thrust + 100 ## clear object
            """           

        else:
            print "Invalid Mode Selected: ", mode


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
        self.targetAlt = 0
        altHold = False
        char = ""

        while 1:
            
            self._set_movement(self.current_roll, self.current_pitch, 0, self.current_thrust)
            
            char = self._getch()
            self.altHold = altHold
            if char == "h":
                print "Auto Pilot ON. Mode = ", self._auto_pilot_mode
                altHold = True
                self.pidctrlr_t.reset()

                if self._auto_pilot_mode != 1:
                	self.targetAlt = self._logger.retrieveVar("baro.asl") ## will throw any error if auto pilot mode == 1 becuase logger will not have been initialised
                
                self.pidctrlr_alt.reset()
                print "Target Alt: ", self.targetAlt
                
            if char == "p":
                if self._motors_on == True:
                    self._motors_on = False
                    print "Motors Now off"
                elif self._motors_on == False:
                    self._motors_on = True
                    print "Motors Now on"

            if altHold == True:
				self._auto_pilot(self._auto_pilot_mode)

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
        self._cf.close_link() ## close connection to crazyflie
    
    
    
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
            try:
                time.sleep(1)
            except (TypeError, IndexError, ZeroDivisionError, IOError, NameError):
                le._turnOffAllProcesses()
                le._cf.close_link()
                le.is_connected = False
                print "Caught type Error" 
        print "Done"
        stop_time = time.time()
        print "Total Flight Time: ", int(stop_time - le.start_time), " seconds"
        ts = time.time()
        dt = datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        # Open a file to write flight time details to
        fo = open("flight_details.txt", "a")
        if le._motors_on == False:
            msg = str(dt + ": " + "Total Flight Time: " + str(int(stop_time - le.start_time)) + " seconds MOTORS OFF\n")
        else:
            msg = str(dt + ": " + "Total Flight Time: " + str(int(stop_time - le.start_time)) + " seconds\n")
        fo.write(msg);

        # Close  file
        fo.close()
        sampRate = 0

        ## plot different data (using Plotter) based on auto pilot mode
        if le._auto_pilot_mode == 1:
            le.plotter1.updateY(le.pidctrlr_t.getErrorAccum(),le.pidctrlr_t.getIncAccum(),le.yPositionReadings, le.batteryReadings, le.pidctrlr_r.getErrorAccum())
            le.writeAll(le.pidctrlr_t.getErrorAccum(),le.pidctrlr_t.getIncAccum(),le.yPositionReadings, le.batteryReadings, le.pidctrlr_r.getErrorAccum())
            print "Time under AutoPilot = ", le.pidctrlr_t.getControlTime(), " seconds"
            sampRate = len(le.pidctrlr_t.getErrorAccum())/le.pidctrlr_t.getControlTime() ## get sampling rate
            print "sampRate = ", sampRate, " samples/seconds"
            le.plotter1.plot()
        elif le._auto_pilot_mode == 2:
            le.plotter1.updateY(le.pidctrlr_alt.getErrorAccum(),le.pidctrlr_alt.getIncAccum(),le.baroReadings, le.batteryReadings,0)
            le.writeAll(le.pidctrlr_alt.getErrorAccum(),le.pidctrlr_alt.getIncAccum(),le.baroReadings, le.batteryReadings,0)
            print "Time under AutoPilot = ", le.pidctrlr_alt.getControlTime(), " seconds"
            le.plotter1.plot()
        else:
            print "Don't plot"

        
    else:
        print "No Crazyflies found, cannot run example"
