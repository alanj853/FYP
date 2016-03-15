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
Simple example that connects to the first Crazyflie found, ramps up/down
the motors and disconnects.
"""

import time, sys, tty, termios, fcntl, os
from threading import Thread

#FIXME: Has to be launched from within the example folder
sys.path.append("../lib")
import cflib
from cflib.crazyflie import Crazyflie

import cflib.crtp
#from cfclient.utils.logconfigreader import LogConfig
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie

import logging

logging.basicConfig(level=logging.ERROR)


class MotorRampExample:
    curr_alt=0;
    current_thrust = 0;
    cf_occupied = False;
    my_list=[]
    _speed_up_mode = "normal"
    
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""
    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print "Connecting to %s" % link_uri

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        
        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        #Thread(target=self._ramp_motors).start()
        Thread(target=self._run_demo).start()
        Thread(target=self._begin_logging).start()

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
            #print "Cannot get Altitude . CF is occupied"

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

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print "Connection to %s failed: %s" % (link_uri, msg)

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print "Connection to %s lost: %s" % (link_uri, msg)

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print "Disconnected from %s" % link_uri
        #self._getAverageAltitude()

    def _run_demo1(self):
        self._current_thrust = 45000
        self._cf.commander.send_setpoint(5, 7, -40, self._current_thrust);
        time.sleep(1);


##        print "\nlanding again"    
##        while self._current_thrust >= 15000:
##            print "Current thrust = ", self._current_thrust
##            roll = self.current_thrust*5/45000;
##            pitch = self.current_thrust*7/45000
##            self._cf.commander.send_setpoint(roll, pitch, 0, self._current_thrust);
##            time.sleep(0.1);
##            self._current_thrust -= 5000;

    def _run_demo(self):
        thrust_mult = 1
        thrust_step = 500
        initial_thrust = 47000
        take_off_thrust = 48000
        self._current_thrust = initial_thrust
        
        print "taking off"
        self._cf.commander.send_setpoint(5, 7, 0, 44000);
        time.sleep(1.0);

        ## at 0:   134.174479339
        ## at 10:  134.414068376
        ## at 20:  134.860107692
        ## at -10: 135.032394366 
        

        print "\nhovering"

        current_time = time.time();
        target_time = current_time + 10;
        while current_time < target_time:
            self._cf.param.set_value('flightmode.althold', "True")
            self._cf.commander.send_setpoint(0, 0, 0, 32767)
            current_time = time.time()
            char = self._getch()
            if char == "w":
                print "pressed w"
                self._cf.commander.send_setpoint(0, 0, 0,( 32767 + 5000))
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, 32767)
            if char == "s":
                print "pressed s"
                self._cf.commander.send_setpoint(0, 0, 0,( 32767 - 5000))
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, 32767)
            if char == "a":
                print "pressed a"
                self._cf.commander.send_setpoint(-10, 0, 0,32767)
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, 32767)
            if char == "d":
                print "pressed d"
                self._cf.commander.send_setpoint(10, 0, 0, 2767)
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, 32767)
            if char == "e":
                break
            
            
##        print "\nlanding again"    
##        while self._current_thrust >= 15000:
##            print "Current thrust = ", self._current_thrust
##            self._set_current_thrust(self._current_thrust);
##            time.sleep(0.1);
##            self._current_thrust -= 5000;
            
        print "done"
        self._current_thrust = 0;
        self._cf.commander.send_setpoint(0, 0, 0, self._current_thrust);
        self._cf.close_link()

    def _getch(self):
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
        c = ""
        try:
            try:
                c = sys.stdin.read(1)
                print "Got character", repr(c)
            except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
            return c;

    def _getInput(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
        finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _set_current_thrust(self, thrust):
        if self.cf_occupied == False:
            #print "can set motors"
            self.cf_occupied = True
            roll = thrust*5/45000;
            pitch = thrust*7/45000;
            print "Current thrust = ", thrust
            print "Current roll = ", roll
            print "Current pitch = ", pitch
            
            if roll > 5:
                roll = 5;
            if pitch > 7:
                pitch = 7
                
            self._cf.commander.send_setpoint(roll, pitch, 0, thrust) # may correct drift problem
            #self._cf.commander.send_setpoint(0, 0, 0, thrust)
            #time.sleep(.1);
            self.cf_occupied = False

    def _speed_up(self, rate):
        print "     speeding up...";
        self._current_thrust = self._current_thrust + 500*rate;
        if self._speed_up_mode =="normal":
            if self._current_thrust >= 50000:
                self._current_thrust = 43000;
                print "limit exceeded"
        else:
            print "in critical mode"
            self._current_thrust = 55000;
            time.sleep(1);
            self._speed_up_mode = "normal"
        self._set_current_thrust(self._current_thrust);

    def _slow_down(self, rate):
        print "     slowing down...";
        self._current_thrust = self._current_thrust - 2000*rate;
        if self._current_thrust < 43000:
            print "         value is too low. Ignoring..."
            self._current_thrust = 43000;
        self._set_current_thrust(self._current_thrust);


    def _getCurrentAltitude(self):
        ## have to assign a temporary thrust while get avverage altitude
        
        self._set_current_thrust(43000);
        
        i = 1;
        alt = self.curr_alt;
        original = alt;
        list1 = []
        curr_time = time.time();
        target_time = curr_time + .25
        while curr_time < target_time:
            if alt != self.curr_alt:
                list1.append(self.curr_alt)
                alt = self.curr_alt
                i += 1
                #print "added ", alt
            curr_time = time.time()
            #if curr_time >=target_time:
                #print "Out of time. only added ", (i-1) , " values" 
                
        try:
            alt = sum(list1)/len(list1)
        except ZeroDivisionError:
            alt = original
        print "Current Altitude = ", alt, " out of ", len(list1), " values"
        self.my_list.append(alt)
        return alt;

    def _getAverageAltitude(self):
        i = 0
        sum = 0
        try:
            greatest_val = self.my_list[0];
            lowest_val = self.my_list[0];
        except IndexError:
            greatest_val = 0;
            lowest_val = 0;
            
        for i in self.my_list:
            sum += i ;
            if abs(i) > abs(greatest_val):
                greatest_val = i;
            if abs(i) < abs(lowest_val):
                lowest_val = i;
        avg = sum/len(self.my_list)
        print "Average altitude value: ", avg
        print "Lowest altitude value: ", lowest_val
        print "Greatest altitude value: ", greatest_val
        print "Variance: ", (greatest_val - lowest_val)
            

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
    else:
        print "No Crazyflies found, cannot run example"


