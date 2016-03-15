
"""
Simple program that allows user to control motors from the keyboard of their machine
IS WORKING
"""

import fcntl
import os
import sys
import termios
from threading import Thread
import time

#FIXME: Has to be launched from within the example folder
sys.path.append("../lib")
import cflib
from cflib.crazyflie import Crazyflie

import cflib.crtp
from cflib.crazyflie import Crazyflie

import logging

logging.basicConfig(level=logging.ERROR)


class MotorRampExample:
    
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

    def _run_demo(self):
        print "\nhovering"

        char = ""
        ##hover_thrust = 32767
        current_thrust = 15000
        while char != "e":
            if current_thrust < 15000:
                current_thrust = 15000
            #self._cf.commander.send_setpoint(0, 0, 0, current_thrust)
            
            char = self._getch()
            if char == "h":
               self._cf.param.set_value('flightmode.althold', "True")
               print "hover ON"
            if char == "j":
               self._cf.param.set_value('flightmode.althold', "False")
               print "hover OFF"
            if char == "o":
               self._cf.commander.send_setpoint(0, 0, 0, 0)
               print "All Motors OFF NOW"
               break
            if char == "w":
                current_thrust = current_thrust + 1000
                print " Increasing thrust. Thrust = ", current_thrust
            if char == "s":
                current_thrust = current_thrust - 1000
                print "Descreasing thrust. Thrust = ", current_thrust
            if char == "\x1b[C":
                print "moving right "
                self._cf.commander.send_setpoint(10, 0, 0, current_thrust)
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, current_thrust)
            if char == "\x1b[D":
                print "moving left "
                self._cf.commander.send_setpoint(-10, 0, 0, current_thrust)
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, current_thrust)
            if char == "\x1b[B":
                print "moving backwards "
                self._cf.commander.send_setpoint(0, -10, 0, current_thrust)
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, current_thrust)
            if char == "\x1b[A":
                print "moving forwards "
                self._cf.commander.send_setpoint(0, 10, 0, current_thrust)
                time.sleep(.25)
                self._cf.commander.send_setpoint(0, 0, 0, current_thrust)
            if char == "l":
                print "pressed l ==> landing..."
                while current_thrust >= 15000:
                    current_thrust = current_thrust - 1000
                    print "     current thrust = ", current_thrust
                    self._cf.commander.send_setpoint(0, 0, 0, current_thrust)
                break
            
            

            
        print "done"
        self._current_thrust = 0;
        self._cf.commander.send_setpoint(0, 0, 0, 0);
        self._cf.close_link()

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
    else:
        print "No Crazyflies found, cannot run example"


