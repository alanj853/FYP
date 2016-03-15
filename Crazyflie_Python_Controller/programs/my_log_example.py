# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2014 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.

"""
Simple example that connects to the first Crazyflie found, logs the Stabilizer
and prints it to the console. After 10s the application disconnects and exits.
"""

import sys
import fcntl
import os
import termios
sys.path.append("../lib")

import cflib.crtp

import logging
import time
from threading import Thread

import cflib.crtp
#from cfclient.utils.logconfigreader import LogConfig
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class LoggingExample:
    curr_alt = 0
    t1 = "";
    t2 = "";
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 5s.
    """
    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """
	

        # Create a Crazyflie object without specifying any cache dirs
        self._cf = Crazyflie()

        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print "Connecting to %s" % link_uri

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        
        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        #Thread(target=self._ramp_motors).start()
        t1 = Thread(target=self.run_demo)
	t2 = Thread(target=self._begin_logging)
	t1.start()
	t2.start()
    def _begin_logging(self):
	print "starting logging..."
        # The definition of the logconfig can be made before connecting
        self._lg_alt = LogConfig(name="Gyro", period_in_ms=10)
        #self._lg_alt.add_variable("baro.asl", "float")
        self._lg_alt.add_variable("gyro.y", "float")

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
        

    def _alt_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print "Error when logging %s: %s" % (logconf.name, msg)

    def _alt_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        #print "[%d][%s]: %s" % (timestamp, logconf.name, data)

        self._analyse_data(data)

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print "Connection to %s failed: %s" % (link_uri, msg)
        self.is_connected = False

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
        #ans = ans*1;
        #print "2nd ans = ", ans
        #ans = int(ans)
        #print "3rd ans = ", ans
        #ans = float(ans)
        #ans = ans/1
        #print "4th ans = ", ans
        self.curr_alt = ans

    def run_demo(self):
	print "Running demo..."
	curr = time.time()
	target = curr + 10
	char = "d"	
	while char != " " and char != "e":
	    print "Gyro x: ", self.curr_alt
	    time.sleep(.25)
            char = self._getch()
	print "Finished Demo"
	self._cf.close_link

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


    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print "Connection to %s lost: %s" % (link_uri, msg)

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print "Disconnected from %s" % link_uri

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
        le = LoggingExample("radio://0/80/250K")
    else:
        print "No Crazyflies found, cannot run example"
