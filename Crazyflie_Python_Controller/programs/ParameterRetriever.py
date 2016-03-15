import logging
from cflib.crazyflie.log import LogConfig

class ParameterRetriever:

    logger = 0;

    def __init__(self, crazyflie):
        print "ParameterRetriever created"
        self._logger = LogConfig(name="MyLogConfig", period_in_ms=10)

    def _begin_logging(self):
        # The definition of the logconfig can be made before connecting
        self._logger.add_variable('baro.asl', "float")

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        self._cf.log.add_config(self._logger)
        if self._logger.valid:
            # This callback will receive the data
            self._logger.data_received_cb.add_callback(self._alt_log_data)
            # This callback will be called on errors
            self._logger.error_cb.add_callback(self._alt_log_error)
            self._logger.start()
        else:
            print("Could not add logconfig since some variables are not in TOC")

    def retrieveVar(self, varName):



    def _alt_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print "Error when logging %s: %s" % (logconf.name, msg)

    def _alt_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        #print "[%d][%s]: %s" % (timestamp, logconf.name, data)
        self._analyse_data(data)
        
    def _convert_data_to_number(self, data , varName):
        # new_data = ""
        # old_data = str(data)
        # for t in old_data.split():
        #     if t.endswith('}'):
        #         new_data= t.replace("}", "") # get rid of last bracket
        # for f in old_data.split():
        #     if f.isspace():
        #         new_data= t.replace(" ", "") # get rid of white space
        # new_data = float(new_data)
        # return new_data

        oldData = str(data)
        if varName in oldData == False:
            return "ERROR: Cannot find '", varName, "' in log data"
        
        oldData = oldData.split(varName + "': ")
        myData = ""
        rhsData = oldData[1]
        for letter in rhsData.split():
            if letter == "}":
                break;
            else:
                myData = myData + letter

        return myData




    def _analyse_data(self, string_data):
        #self.curr_alt = self._convert_data_to_number(string_data)
        ans = self._convert_data_to_number(string_data, varName)
        self.curr_alt = ans
        print "varName = ", ans