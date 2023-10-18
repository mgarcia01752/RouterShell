import logging
from typing import List

from lib.common.common import Common
from lib.network_manager.run_commands import RunCommand
from lib.common.constants import *

from enum import Enum, auto

class State(Enum):
    UP = 'up'
    DOWN = 'down'
    
class Duplex(Enum):
    
    AUTO = "auto"
    """
    Auto-negotiation (Auto): In auto-negotiation mode, the device negotiates with 
    its link partner to determine the best duplex mode to use. Auto-negotiation is recommended 
    for most modern networks as it allows devices to automatically adapt to the highest common denominator.
    """

    HALF = "half"
    """
    Half Duplex (Half): In half-duplex mode, a network interface can either transmit or receive data at a time, but not both simultaneously. 
    This mode is typically used for older networks or when compatibility with legacy equipment is required.
    """

    FULL = "full"
    """
    Full Duplex (Full): In full-duplex mode, a network interface can transmit and receive data simultaneously. 
    This mode is typically used for high-speed connections where there is a dedicated channel 
    for both sending and receiving data. It minimizes collisions and improves network performance.
    """

class Speed(Enum):
    MBPS_10 = 10
    """
    10 MBPS: Configures the interface to operate at a fixed speed of 10 megabits per second (Mbps).
    """

    MBPS_100 = 100
    """
    100 MBPS: Configures the interface to operate at a fixed speed of 100 megabits per second (Mbps).
    """

    MBPS_1000 = 1000
    """
    1000 MBPS: Configures the interface to operate at a fixed speed of 1 gigabit per second (Mbps).
    """

    MBPS_10000 = 10000
    """
    1000 MBPS: Configures the interface to operate at a fixed speed of 10 gigabits per second (Mbps).
    """

    AUTO_NEGOTIATE = True
    """
    AUTO-NEGOTIATE: In auto-negotiation mode, the device negotiates with its link partner to determine the 
    best speed and duplex mode to use within the limits supported by both devices.
    """
        
class PhyServiceLayer(RunCommand):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
    def set_duplex(self, ifName: str, duplex: Duplex):
        """
        Set the duplex mode of a network interface.

        Args:
            ifName (str): The name of the network interface.
            duplex (Duplex): The desired duplex mode to set for the interface (e.g., Duplex.DUPLEX_AUTO).

        Returns:
            bool: True if the duplex mode is successfully set, False otherwise.
        """
        if duplex is Duplex.AUTO:
            self.log.debug(f"do_duplex() - duplex set to auto")
            cmd = ['ethtool', '-s', ifName, 'autoneg' , 'on']
        else:
            cmd = ['ethtool', '-s', ifName, 'duplex', duplex.value]

        status = self.run(cmd).exit_code

        if status == STATUS_OK:
            self.log.debug(f"Set duplex mode of {ifName} to {duplex.name}")
            return True
        else:
            self.log.error(f"Failed to set duplex mode of {ifName} to {duplex.name}")
            return False
    
    def set_ifSpeed(self, ifName: str, ifSpeed: Speed, auto: bool = False):
        """
        Set the speed of a network interface and optionally enable or disable auto-negotiation.

        Args:
            ifName (str): The name of the network interface.
            ifSpeed (Speed): The desired speed to set for the interface.
            autoneg (bool, optional): Whether to enable (True) or disable (False) auto-negotiation. Defaults to False.

        Returns:
            bool: True if the speed is successfully set, False otherwise.
        """
        
        cmd_auto = ['ethtool', '-s', ifName, 'autoneg', 'on' if auto else 'off']
        '''Update both variable, its the same as updating one and makes the return less complicated'''
        status_speed = status_auto = self.run(cmd_auto).exit_code   
        
        if not auto:
            cmd_speed = ["ethtool", "-s", ifName, "speed", str(ifSpeed.value)]
            
            status_speed = self.run(cmd_speed).exit_code
            
            if status_speed == STATUS_OK:
                self.log.debug(f"Set speed of {ifName} to {ifSpeed.name}")
            else:
                self.log.error(f"Failed to set speed of {ifName} to {ifSpeed.name}")

        if status_auto == STATUS_OK:
            if auto:
                self.log.debug(f"Enabled auto-negotiation on {ifName}")
            else:
                self.log.debug(f"Disabled auto-negotiation on {ifName}")
        else:
            self.log.error(f"Failed to set auto-negotiation on {ifName} to {'on' if auto else 'off'}")

        return status_speed == STATUS_OK and status_auto == STATUS_OK

    def set_interface_state(self, ifName: str, state: State) -> bool:
        """
        Change the state of a network interface.

        :param ifName: The name of the network interface.
        :param state: The desired state of the network interface (State.UP or State.DOWN).
        :type ifName: str
        :type state: State
        :return: True if the state change was successful, False otherwise.
        :rtype: bool
        """
        self.log.debug(f"set_interface_state() -> ifName: {ifName} -> state: {state}")
        
        if state not in (State.UP, State.DOWN):
            self.log.error("Invalid state. Use State.UP or State.DOWN.")
            return False

        cmd = ['ip', 'link', 'set', 'dev', ifName, state.value]

        status = self.run(cmd).exit_code

        if not status:
            self.log.debug(f"Changed state of {ifName} to {state.value}")
        else:
            self.log.error(f"Failed to change state of {ifName} to {state.value}")

        return status == STATUS_OK 

    
    def set_mtu(self, ifName: str, mtu_size: int) -> bool:
        """
        Set the Maximum Transmission Unit (MTU) size for a network interface using iproute2.

        Args:
            ifName (str): The name of the network interface to configure.
            mtu_size (int): The MTU size to set for the interface.

        Returns:
            bool: True if the MTU size was unsuccessfully set, False otherwise.

        """
        # Run the iproute2 command to set the MTU size
        if self.run(['ip', 'link', 'set', ifName, 'mtu', str(mtu_size)]).exit_code:
            return STATUS_NOK
        else:
            return STATUS_OK
    

        
