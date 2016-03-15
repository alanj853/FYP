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
Simple scripted escape
"""

import time, sys
from threading import Thread

#FIXME: Has to be launched from within the example folder
sys.path.append("../lib")

import logging
 
import cflib.crtp
from cfclient.utils.logconfigreader import LogConfig
from cfclient.utils.logconfigreader import LogVariable
from cflib.crazyflie import Crazyflie
 
logging.basicConfig(level=logging.DEBUG)




class Main:
    """
    Class is required so that methods can access the object fields.
    """
    def __init__(self):
        """
        Connect to Crazyflie, initialize drivers and set up callback.
 
        The callback takes care of logging the accelerometer values.
        """
        self.crazyflie = Crazyflie()
        cflib.crtp.init_drivers()
 
        self.crazyflie.connectSetupFinished.add_callback(
                                                    self.connectSetupFinished)
 
        self.crazyflie.open_link("radio://0/80/250K")
 
    def connectSetupFinished(self, linkURI):
        """
        Configure the logger to log accelerometer values and start recording.
 
        The logging variables are added one after another to the logging
        configuration. Then the configuration is used to create a log packet
        which is cached on the Crazyflie. If the log packet is None, the
        program exits. Otherwise the logging packet receives a callback when
        it receives data, which prints the data from the logging packet's
        data dictionary as logging info.
        """
        # Set stabilizer logging config
        stab_log_conf = LogConfig("stabilizer", 10)
        stab_log_conf.addVariable(LogVariable("stabilizer.roll", "float"))
        stab_log_conf.addVariable(LogVariable("stabilizer.pitch", "float"))
        stab_log_conf.addVariable(LogVariable("stabilizer.yaw", "float"))
 
        # Now that the connection is established, start logging
        self.stab_log = self.crazyflie.log.create_log_packet(stab_log_conf)
 
        if self.stab_log is not None:
            self.stab_log.dataReceived.add_callback(self.log_stab_data)
            self.stab_log.start()
        else:
            print("acc.x/y/z not found in log TOC")
 
    def log_stab_data(self, data):
        logging.info("Stabilizer: Roll=%.2f, Pitch=%.2f, Yaw=%.2f" %
                        (data["stabilizer.roll"], data["stabilizer.pitch"], data["stabilizer.yaw"]))
 
Main()
