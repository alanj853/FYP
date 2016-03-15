"""
Used for sending control setpoints to the Crazyflie
"""

__author__ = 'Bitcraze AB'
__all__ = ['Commander']

from cflib.crtp.crtpstack import CRTPPacket, CRTPPort
import struct


class Commander():
    """
    Used for sending control setpoints to the Crazyflie
    """

    def __init__(self, crazyflie=None):
        """
        Initialize the commander object. By default the commander is in
        +-mode (not x-mode).
        """
        self._cf = crazyflie
        self._x_mode = False

    def set_client_xmode(self, enabled):
        """
        Enable/disable the client side X-mode. When enabled this recalculates
        the setpoints before sending them to the Crazyflie.
        """
        self._x_mode = enabled

    def send_setpoint(self, roll, pitch, yaw, thrust, hover):
        """
        Send a new control setpoint for roll/pitch/yaw/thust to the copter

        The arguments roll/pitch/yaw/trust is the new setpoints that should
        be sent to the copter
        
        Added hover parameter for purposes of project
        
        """
        if self._x_mode:
            roll = 0.707 * (roll - pitch)
            pitch = 0.707 * (roll + pitch)

        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER
        pk.data = struct.pack('<fffH?', roll, -pitch, yaw, thrust, hover)
        self._cf.send_packet(pk)
