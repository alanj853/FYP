
"""
Simple program that allows user to control motors from the keyboard of their machine
IS WORKING

ONLY OPEN IN SUBLIME TEXT as other programs might fuck up the format
"""

import socket
import os
import sys
from threading import Thread
import time, math
from datetime import datetime, date

#FIXME: Has to be launched from within the example folder
sys.path.append("../lib")
import cflib
from cflib.crazyflie import Crazyflie

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

import logging
#from Tkinter import *
#import tkMessageBox
#import Tkinter



logging.basicConfig(level=logging.ERROR)


class FlightController:
    is_connected = False ## is connected to PC via radio
    best_matrix = "Not Assigned" ## the sub frame with the most free space -- see documentation
    turn_off_UDP_client = False;
    _motors_on = True; ## variable for motors on
    _client_ready = False 
    windows_linux = "linux" ## type of machine client is running on
    curr_alt = 45;
    log_battery = True
    start_time = 0



    # init function to connect to crazyflie
    def __init__(self, link_uri):
        #Initialize and run the example with the specified link_uri """
        self.is_connected = True
        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print "Connecting to %s" % link_uri

    ## this method is called when a successful connection to the CF has been made
    def _connected(self, link_uri):

        Thread(target=self._motor_controller).start() # start the thread for controlling the motors
        Thread(target=self._start_gui).start()
        Thread(target=self._begin_logging).start()
        #self._start_gui();
        
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
        self.log_battery = False;

    # function to control UDP communication with server
    def _UDP_Client(self):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 4446
        MESSAGE = "CF:Client-Request_Coordinates"
        BUFFER_SIZE = 256
         
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "Sending Message:", MESSAGE
        x = "Not assigned"

        self._client_ready = True;
        i = 0;
        data = ""
        
        while(self.turn_off_UDP_client == False) :
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP # nternet
            sock.connect((UDP_IP, UDP_PORT)) ## connect to port and host
            sock.sendto(MESSAGE,(UDP_IP, UDP_PORT)) ## send message to request data from server
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            self.best_matrix = data
            time.sleep(.25);

        sock.close()
        print "Client Closed"


    def _begin_logging(self):
        # The definition of the logconfig can be made before connecting
        self._lg_alt = LogConfig(name="Altitude", period_in_ms=10)
        self._lg_alt.add_variable("pm.vbat", "float")
        #self._lg_alt.add_variable('motor.m1', "float")
        #self._lg_alt.add_variable('motor.m2', "float")
        #self._lg_alt.add_variable('motor.m3', "float")
        #self._lg_alt.add_variable('motor.m4', "float")
        #elf._lg_alt.add_variable("gyro.x", "float")

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        self._cf.log.add_config(self._lg_alt)
        if self._lg_alt.valid:
            # This callback will receive the data
            self._lg_alt.data_received_cb.add_callback(self._alt_log_data)
            # This callback will be called on errors
            self._lg_alt.error_cb.add_callback(self._alt_log_error)
            self._lg_alt.start()
        else:
            print("Could not add logconfig since some variables are not in TOC")

    #curr_alt = 0
    cf_occupied = False

    def _alt_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print "Error when logging %s: %s" % (logconf.name, msg)

    def _alt_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        #print "[%d][%s]: %s" % (timestamp, logconf.name, data)

        if self.cf_occupied == False:
            #print "can get alt"
            self.cf_occupied = True
            self._analyse_data(data)
            self.cf_occupied = False
        else:
            x=4
            print "Cannot get Altitude . CF is occupied"

    def _convert_data_to_number(self, data):
        new_data = ""
        old_data = str(data)
        for t in old_data.split():
            if t.endswith('}'):
                new_data= t.replace("}", "") # get rid of last bracket
        for f in old_data.split():
            if f.isspace():
                new_data= t.replace(" ", "") # get rid of white space
        new_data = float(new_data)
        return new_data

    def _analyse_data(self, string_data):
        #self.curr_alt = self._convert_data_to_number(string_data)
        ans = self._convert_data_to_number(string_data)
        #print "1st ans = ", ans
        ans = ans*1000;
        #print "2nd ans = ", ans
        ans = int(ans)
        #print "3rd ans = ", ans
        ans = float(ans)
        ans = ans/1000
        #print "4th ans = ", ans
        self.curr_alt = ans

    #  GUI To Diplay Battery info
    def _start_gui(self):
        # root = Tk()
        # root.geometry('400x100+20+20')
         
        # mainframe = Frame(root)
        # mainframe.grid(column=1000, row=1000, sticky=(N, W, E, S))
        # mainframe.columnconfigure(0, weight=1)
        # mainframe.rowconfigure(0, weight=1)
         
        # best = StringVar()
        # best.set('start')
        # x1 = 12
        # Label(mainframe,textvariable=best,bg='#321000',fg='#000fff000',font=("Helvetica",x1)).grid(column=1,row=1)
         
        # while self.log_battery == True:
        #     time.sleep(1.0)
        #     ans = 100*self.curr_alt/4
        #     battery_info = "Battery Voltage = ", self.curr_alt, "\n", "Percentage = ", ans, "%"
        #     best.set(battery_info)
        #     mainframe.update()
        # root.mainloop() 
        x = 5

    # auto pilot function
    def _auto_pilot(self, curr_thrust, curr_roll, curr_pitch):
        #t = Thread(target=self._UDP_Client);
        #t.start()
        #while(self._client_ready ==False):
            # wait for client thread to start
        #    x=4; ## I had to put some outcome here for while loop to work. x =4 does nothing


        
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
        #t.stop()
        print "Done AutoPilot"
        #print "target x =", self.target_x


    # function to set thrust, roll, pitch and yaw parameters on crazyflie    
    def _set_movement(self,roll, pitch, yaw, thrust):
        if self._motors_on == True:
            self._cf.commander.send_setpoint(roll, pitch, yaw, thrust)

        
    def _motor_controller(self):
        self._print_controls()
        self.start_time = time.time()
        calib_r = 0
        calib_p = 0
        current_thrust = 15000
        
        char = ""
        while 1:
            if current_thrust < 15000:
                current_thrust = 15000
            self._set_movement(calib_r, calib_p, 0, current_thrust)
            
            char = self._getch()

            if char == "h":
                print "hover ON"
                self._cf.param.set_value('flightmode.althold', "True")
                #self._auto_pilot(current_thrust, calib_r, calib_p)
               
            if char == "j":
                print "hover OFF"
                self._cf.param.set_value('flightmode.althold', "False")

	        ## Emergency Brake! Turns all motors off immediately. No soft landing
            if char == "o":
               self._set_movement(0, 0, 0, 0)
               print "All Motors OFF NOW"
               break

	        ## Thrust Control
            if char == "q":
                current_thrust = 44000
                print "Take-off thrust. Thrust = ", current_thrust
            if char == "w":
                current_thrust = current_thrust + 50
                print "Increasing thrust. Thrust = ", current_thrust
            if char == "s":
                current_thrust = current_thrust - 50
                print "Descreasing thrust. Thrust = ", current_thrust


	        ## For Big Thrust Increments/Decrements
            if char == "t":
                current_thrust = current_thrust + 500
                print "Increasing thrust. Thrust = ", current_thrust
            if char == "g":
                current_thrust = current_thrust - 500
                print "Descreasing thrust. Thrust = ", current_thrust
            if char == "b":
                current_thrust = current_thrust + 5000
                print "Boost of 5000. Thrust = ", current_thrust
            if char == "n":
                current_thrust = current_thrust - 5000
                print "DeBoost of 5000. Thrust = ", current_thrust

            ## Roll control
            if char == "\x1b[C" or char == "M": ## this is the right arrow on the keyboard translation
                print "moving right "
                self._set_movement(15, calib_p, 0, current_thrust)
                time.sleep(.25)
                calib_r += .5
                print "     roll changed to: ", calib_r
                self._set_movement(calib_r, calib_p, 0, current_thrust)
            if char == "\x1b[D" or char == "K":
                print "moving left "
                self._set_movement(-15, calib_p, 0, current_thrust)
                time.sleep(.25)
                calib_r -= .5
                print "     roll changed to: ", calib_r
                self._set_movement(calib_r, calib_p, 0, current_thrust)

            ## Pitch Control
            if char == "\x1b[B" or char == "P":
                print "moving backwards "
                self._set_movement(calib_r, -15, 0, current_thrust)
                time.sleep(.25)
                calib_p -= .5
                print "     pitch changed to: ", calib_p
                self._set_movement(calib_r, calib_p, 0, current_thrust)
            if char == "\x1b[A" or char == "H":
                print "moving forwards "
                self._set_movement(calib_r, 15, 0, current_thrust)
                time.sleep(.25)
                calib_p += .5
                print "     pitch changed to: ", calib_p
                self._set_movement(calib_r, calib_p, 0, current_thrust)

    	    ## Yaw Control	    
    	    if char == "a":
                print "turning left"
                self._set_movement(calib_r, calib_p, -50, current_thrust)
                time.sleep(.25)
                self._set_movement(calib_r, calib_p, 0, current_thrust)
    	    if char == "d":
        		print "turning right"
        		self._set_movement(calib_r, calib_p, 50, current_thrust)
                        time.sleep(.25)
        		self._set_movement(calib_r, calib_p, 0, current_thrust)
	    
	        ## Landing
            if char == "l":
                print "pressed l ==> landing..."
                l_char = self._getch()
                while current_thrust >= 15000 and l_char != "\n":
                    current_thrust = current_thrust - 750
                    print "     current thrust = ", current_thrust
                    self._set_movement(calib_r, calib_p, 0, current_thrust)
                    l_char = self._getch()
                    time.sleep(.5)
                #break
	   
            ## Enter. Press "Enter" when cf has been calibrated
            if char == "\n":
                print "Calibration Done"
                break
                
        params = []
        params.append(calib_r);
        params.append(calib_p);
        params.append(current_thrust)
        
        print "Sent Roll = ", calib_r
        print "Sent Pitch = ", calib_p
        print "Sent Thrust = ", current_thrust
        self._cf.close_link()
        return params;
    
    
    
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
        msg = str(dt + ": " + "Total Flight Time: " + str(int(stop_time - le.start_time)) + " seconds\n")
        fo.write(msg);

        # Close opened file
        fo.close()
        le.turn_off_UDP_client = True;
    else:
        print "No Crazyflies found, cannot run example"
