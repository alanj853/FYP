
"""
Simple program that allows user to control motors from the keyboard of their machine
IS WORKING

ONLY OPEN IN SUBLIME TEXT
"""

import fcntl
import os
import sys
import termios
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

logging.basicConfig(level=logging.ERROR)


class MotorRampExample:
    is_connected = False
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""
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

    def _connected(self, link_uri):

        #This callback is called form the Crazyflie API when a Crazyflie
        #has been connected and the TOCs have been downloaded."""

        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        #Thread(target=self._ramp_motors).start()
        Thread(target=self._calibrate).start()
        Thread(target=self._begin_logging).start()
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

    def _begin_logging(self):
        # The definition of the logconfig can be made before connecting
        self._lg_alt = LogConfig(name="Altitude", period_in_ms=10)
        self._lg_alt.add_variable("baro.asl", "float")
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

    curr_alt = 0
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
        self.curr_alt = self._convert_data_to_number(string_data)

    def _hover(self):
        xt = self.target_x;
        yt = self.target_y;
        xc = self.current_x;
        yc = self.current_y;




    def _hover(self, thrust, roll, pitch):
        alt = self._getCurrentAltitude()
        print "-----------------------------------------------"
        print "--------------TARGET ALTITUDE------------------"
        print "------------------", alt ,"--------------------"
        print "-----------------------------------------------"


        roll_r = roll + 5
        roll_l = roll - 5
        pitch_b = pitch - 5
        pitch_f = pitch + 5
        char = self._getch()
        old_thrust = thrust # for reference
        while char != "j":
            thrust = self._determine_thrust(thrust, old_thrust, alt)
            #self._cf.commander.send_setpoint(roll, pitch, 0, thrust)
            self._cf.commander.send_setpoint(0, 0, 0, thrust)
            print "Thrust = ", thrust, " Roll = ", roll, " Pitch = ", pitch
            time.sleep(.1)
            char = self._getch()
        print "-----------------------------------------------"
        print "--------------------DONE----------------------."
        print "-----------------------------------------------"	    


    def _determine_thrust(self, curr_thrust, old_thrust, target_alt):
    	alt = self._getCurrentAltitude()
        if curr_thrust < (old_thrust - 7500) or curr_thrust > (old_thrust + 3000): ## capping
    	    return old_thrust
    	elif alt < target_alt:
                return (curr_thrust + 10)
    	elif alt > target_alt:
    	    return (curr_thrust - 10)
    	else:
    	    return curr_thrust;


    alt_values = []
    alt_average = 0
    def _getCurrentAltitude(self):
        i = 1;
        alt = self.curr_alt;
        original = alt;
        list1 = []
        curr_time = time.time();
        target_time = curr_time + .4
        if len(self.alt_values) < 100:
            print "should only be called once!"
            while len(self.alt_values) < 100:
            	self.alt_values.append(self.curr_alt)
                print "added ", self.curr_alt
            try:
                self.alt_average = sum(self.alt_values)/len(self.alt_values)

            except ZeroDivisionError:
                return original
	    #print "Current Altitude = ", alt_average, " out of ", len(alt_values), " values"
	    return self.alt_average
    	elif len(self.alt_values) >= 100:
    	    self.alt_values.append(self.curr_alt)
    	    self.alt_values.pop(0)
    	    try:
                self.alt_average = sum(self.alt_values)/len(self.alt_values)
    		
            except ZeroDivisionError:
                return original

    	    print "Current Altitude = ", self.alt_average, " out of ", len(self.alt_values), " values"
    	    return self.alt_average
	
        #print "1st alt = ", alt
        #alt = alt*10;
        #print "2nd alt = ", alt
        #alt = int(alt)
        #print "3rd alt = ", alt
        #alt = float(alt)
        #alt = alt/10
        #print "4th alt = ", alt
        #alt = self._determine_alt(alt)
        #print "Current Altitude = ", alt, " out of ", len(list1), " values"
        #return alt;
    
    def _determine_alt(self, alt):
        upper = math.ceil(alt)
    	lower = math.floor(alt)
    	middle = (upper + lower )/ 2
    	#print "Upper: ", upper, " Lower: ", lower, " Middle: ", middle
    	diff_u = abs(upper - alt)
    	diff_l = abs(lower - alt)
    	diff_m = abs(middle - alt)
    	list1 = []
    	list1.append(diff_u)
    	list1.append(diff_l)
    	list1.append(diff_m)
    	if diff_u == min(list1):
    	    return upper; 
    	if diff_l == min(list1):
    	    return lower;
    	if diff_m == min(list1):
    	    return middle;   
        
    def _calibrate(self):
        self._print_controls()

        calib_r = 0
        calib_p = 0
        current_thrust = 15000
        
        char = ""
        while 1:
            if current_thrust < 15000:
                current_thrust = 15000
            self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)
            
            char = self._getch()
            if char == "h":
                print "hover ON"
                self._hover(current_thrust, calib_r, calib_p)
               
            if char == "j":
                print "hover OFF"
                self._cf.param.set_value('flightmode.althold', "False")

	        ## Emergency Brake! Turns all motors off immediately. No soft landing
            if char == "o":
               self._cf.commander.send_setpoint(0, 0, 0, 0)
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
                current_thrust = current_thrust + 10000
                print "Boost of 10000. Thrust = ", current_thrust
            if char == "n":
                current_thrust = current_thrust - 5000
                print "DeBoost of 5000. Thrust = ", current_thrust

            ## Roll control
            if char == "\x1b[C": ## this is the right arrow on the keyboard translation
                print "moving right "
                self._cf.commander.send_setpoint(15, calib_p, 0, current_thrust)
                time.sleep(.25)
                calib_r += .5
                print "     roll changed to: ", calib_r
                self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)
            if char == "\x1b[D":
                print "moving left "
                self._cf.commander.send_setpoint(-15, calib_p, 0, current_thrust)
                time.sleep(.25)
                calib_r -= .5
                print "     roll changed to: ", calib_r
                self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)

            ## Pitch Control
            if char == "\x1b[B":
                print "moving backwards "
                self._cf.commander.send_setpoint(calib_r, -15, 0, current_thrust)
                time.sleep(.25)
                calib_p -= .5
                print "     pitch changed to: ", calib_p
                self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)
            if char == "\x1b[A":
                print "moving forwards "
                self._cf.commander.send_setpoint(calib_r, 15, 0, current_thrust)
                time.sleep(.25)
                calib_p += .5
                print "     pitch changed to: ", calib_p
                self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)

    	    ## Yaw Control	    
    	    if char == "a":
                print "turning left"
                self._cf.commander.send_setpoint(calib_r, calib_p, -50, current_thrust)
                time.sleep(.25)
                self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)
    	    if char == "d":
        		print "turning right"
        		self._cf.commander.send_setpoint(calib_r, calib_p, 50, current_thrust)
                        time.sleep(.25)
        		self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)
	    
	        ## Landing
            if char == "l":
                print "pressed l ==> landing..."
                l_char = self._getch()
                while current_thrust >= 15000 and l_char != "\n":
                    current_thrust = current_thrust - 750
                    print "     current thrust = ", current_thrust
                    self._cf.commander.send_setpoint(calib_r, calib_p, 0, current_thrust)
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


    def _getch(self):
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
        #le = MotorRampExample(available[0][0])
        le = MotorRampExample("radio://0/80/250K")
        start_time = time.time()
        while le.is_connected:
            time.sleep(1)
        print "Done"
        stop_time = time.time()
        print "Total Flight Time: ", int(stop_time - start_time), " seconds"
        ts = time.time()
        dt = datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        # Open a file to write flight details to
        fo = open("flight_details.txt", "a")
        msg = str(dt + ": " + "Total Flight Time: " + str(int(stop_time - start_time)) + " seconds\n")
        fo.write(msg);

        # Close opend file
        fo.close()
    else:
        print "No Crazyflies found, cannot run example"
