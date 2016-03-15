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

import time, sys
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
        self._getAverageAltitude()

    def _run_demo1(self):
        self._cf.commander.send_setpoint(13, 13.75, 0, 45000);
        time.sleep(2);
        self._cf.commander.send_setpoint(0, 0, 0, 0);

    def _run_demo(self):
        thrust_mult = 1
        thrust_step = 500
        initial_thrust = 47000
        take_off_thrust = 48000
        self._current_thrust = initial_thrust
        
        print "taking off"
        #self._cf.commander.send_setpoint(13, 3, 0, 44000);
        time.sleep(2.0);

        ## at 0:   134.174479339
        ## at 10:  134.414068376
        ## at 20:  134.860107692
        ## at -10: 135.032394366 
        

        print "\nhovering"
        self._hover(3);
            
            
        print "\nlanding again"    
##        while self._current_thrust >= 15000:
##            print "Current thrust = ", self._current_thrust
##            self._set_current_thrust(self._current_thrust);
##            time.sleep(0.1);
##            self._current_thrust -= 10000;
            
        print "done"
        self._current_thrust = 0;
        self._cf.commander.send_setpoint(0, 0, 0, self._current_thrust);
        self._cf.close_link()

    def _hover(self, time_in_seconds):
        print "-----------------------------------------------"
        print "--------------TARGET ALTITUDE------------------"
        target_alt = abs(self._getCurrentAltitude());
        #target_alt = 146.716658959
        print "-----------------------------------------------"
        print "-----------------------------------------------"
        time.sleep(.1);
        current_time = time.time();
        target_time = current_time + time_in_seconds;
        print "Current Time = ", current_time, ". Finish Time =  ", target_time
        
        while current_time <= target_time:
            current_alt = abs(self._getCurrentAltitude());
            current_time = time.time();
            if current_alt < target_alt:
                diff = target_alt - current_alt
                print "diff between target and current is: ", -1*diff
                if diff < 2:
                    if diff > .5:
                        self._speed_up(diff);
                        self._speed_up_mode = "normal"
                    else:
                        print "         difference is negligable"
                else:
                    self._speed_up(diff)
                    self._speed_up_mode = "critical"
            elif current_alt > target_alt:
                diff = current_alt - target_alt
                print "diff between target and current is: ", diff
                if diff < 1:
                    if diff > .01:
                        self._slow_down(diff*1.5);
                    else:
                        print "         difference is negligable"
                else:
                    self._slow_down(1)
            else:
                print "     Perfect thrust assinged. You are now hovering!!!";
        print "-----------------------------------------------"
        print "--------------------DONE----------------------."
        print "-----------------------------------------------"
        


    def _set_current_thrust(self, thrust):
        if self.cf_occupied == False:
            #print "can set motors"
            self.cf_occupied = True
            print "Current thrust = ", thrust
            roll = 13;
            pitch = 13.75;
            #self._cf.commander.send_setpoint(roll, pitch, 0, thrust) # may correct drift problem
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

    def _speed_up1(self, rate):
        print "     speeding up...";
        if self._current_thrust >= 50000:
            self._current_thrust = 45000;
            print "limit exceeded"
        else:
            if self._current_thrust < 45000:
                print "         Thrust is very low. Need to speed up Fast!"
                self._current_thrust = 49000;
                time.sleep(.1)
            else:
                self._current_thrust = self._current_thrust + 500*rate;
        self._set_current_thrust(self._current_thrust);

    def _slow_down1(self, rate):
        print "     slowing down...";
        self._current_thrust = self._current_thrust - 2000*rate;
        if self._current_thrust < 42000:
            print "         value is too low. Ignoring..."
            self._current_thrust = 42000;
        self._set_current_thrust(self._current_thrust);


    def _getCurrentAltitude(self):
        print "Current Altitude = ", self.curr_alt
        self.my_list.append(self.curr_alt)
        return self.curr_alt;

    def _getAverageAltitude(self):
        i = 0
        sum = 0
        greatest_val = self.my_list[0];
        lowest_val = self.my_list[0];
        for i in self.my_list:
            sum += i ;
            if i > greatest_val:
                greatest_val = i;
            if i < lowest_val:
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


