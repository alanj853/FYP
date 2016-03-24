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
sys.path.append("../lib")
sys.path.append("C:\Python27\Lib\site-packages")

import cflib.crtp

import logging
import time
from threading import Timer
from threading import Thread
from UDP_Client import UDP_Client
from Logger import Logger
from Plotter import Plotter

import time, math
from datetime import datetime, date
import matplotlib.pyplot as plt
import numpy as np

import cflib.crtp
from cfclient.utils.logconfigreader import LogConfig
from cflib.crazyflie import Crazyflie

from random import randint
from SubPlot import SubPlot

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class LoggingExample:
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 5s.
    """



    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        # Create a Crazyflie object without specifying any cache dirs
        self._cf = Crazyflie()
        self.logger = Logger(self._cf)
        self.logger.logNewVar("baro.asl","float")
        self.logger.logNewVar("gyro.x","float")
        self.logger.logNewVar("gyro.y","float")

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

        self.plot1 = Plotter("Time vs Distance")
        

    def _connected(self, link_uri):

        print "Connected to %s" % (link_uri)

        ## UDP TEST. Note to run this test you will need to first run a UDP server

        # udpClient = UDP_Client("127.0.0.1", 5000)
        # data = udpClient.requestData()
        # print "Data = ", data
        # self._cf.close_link()

        ########## Logger TEST ##########

        # thread1 = Thread(target=self.logger._begin_logging)
        # thread1.start()
        # thread2 = Thread(target=self._test)
        # thread2.start()


        ########## Plotter TEST ##################


        thread1 = Thread(target=self.plot1.plot)
        thread2 = Thread(target=self._test)
        thread1.start()
        thread2.start()
        
        #self._cf.close_link()


        
        	
        
    def _test(self):
        char = self._getch()
        count  = 0
        while char != "d":
            #self.logger.retrieveVars(["gyro.x","baro.asl","gyro.y"])
            char = self._getch()
            yValue = randint(-10,10)

            self.plot1.X1.append(count)
            self.plot1.Y1.append(yValue)
            self.plot1.XMin1 = 0
            self.plot1.XMax1 = count
            self.plot1.YMin1 = -10
            self.plot1.YMax1 = 10

            self.plot1.X2.append(count)
            self.plot1.Y2.append(-1*yValue)
            self.plot1.XMin2 = 0
            self.plot1.XMax2 = count
            self.plot1.YMin2 = -10
            self.plot1.YMax2 = 10



            count = count + 1



        self.plot1.closePlot = True


        self._cf.close_link()

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


    windows_linux = "windows"
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
        #le = LoggingExample(available[0][0])
        le = LoggingExample("radio://0/80/250K")
    else:
        print "No Crazyflies found, cannot run example"

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    while le.is_connected:
        time.sleep(1)
