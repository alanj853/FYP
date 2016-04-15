"""
Class for logging data from Crazyflie. It uses an old logging framework
implemented by bitcraze, however it parse the data logged to retieve
individual log parameters
"""

import logging
from cflib.crazyflie.log import LogConfig
from threading import Thread

logging.basicConfig(level=logging.ERROR)

class Logger:

    def __init__(self, crazyflie):
        print "Logger created"
        self._logger = LogConfig(name="MyLogConfig", period_in_ms=10)
        self._cf = crazyflie
        self.cfData = "not used"
        self.loggingStarted = False
        
    def _begin_logging(self):
        print "Starting logger..."

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        #self._logger.add_variable("baro.asl", "float")
        self._cf.log.add_config(self._logger)
        if self._logger.valid:
            # This callback will receive the data
            self._logger.data_received_cb.add_callback(self._alt_log_data)
            # This callback will be called on errors
            self._logger.error_cb.add_callback(self._alt_log_error)
            
            self._logger.start()
            print "Logger Started"
            
        else:
            print "Could not add logconfig since some variables are not in TOC"
            print "Log not started"

    ## in order to log data, the user must specify what data to log. See implementation in main.py
    def logNewVar(self, varName, numberType):
        self._logger.add_variable(varName, numberType) ## add a logable  parameter to logConfig object. Number type is usually "float". example: self._logger.add_variable('baro.asl', "float")
        #self._logger.add_variable("baro.asl", "float")
        #self._logger.add_variable("gyro.x", "float")
        print "Var '", varName, "' of type '", numberType, "' added to Logger"


    def _alt_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print "Error when logging %s: %s" % (logconf.name, msg)

    def _alt_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        #print "[%d][%s]: %s" % (timestamp, logconf.name, data)
        self.loggingStarted = True
        self.cfData = data
        
        
    def _convert_data_to_number(self, data , varName):
        #print " in _convert_data_to_number"
        oldData = str(data)
        if oldData == "":
            return "ERROR: no data"

        if varName in oldData == False:
            return "ERROR: Cannot find '", varName, "' in log data"
        
        oldData = oldData.split(varName + "': ")
        myData = ""

        rhsData = list(oldData[1])
        for letter in rhsData:
            if letter == '}' or letter == ',':
                break;
            else:
                myData = myData + letter

        return float(myData)




    def retrieveVar(self, varName):
        ans = self._convert_data_to_number(self.cfData, varName)
        #print varName ," = ", ans
        return ans

    def retrieveVars(self, varNames):
        newVars = []
        for varName in varNames:
            ans = self._convert_data_to_number(self.cfData, varName)
            print varName ," = ", ans
            newVars.append(ans)
        print ""
        return newVars