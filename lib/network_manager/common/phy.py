import logging
from typing import List

from lib.common.common import Common
from lib.network_manager.common.run_commands import RunCommand
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
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
        self.log.setLevel(RSLGS().PHY)
        
    def set_duplex(self, interface_name: str, duplex: Duplex):
        """
        Set the duplex mode of a network interface.

        Args:
            interface_name (str): The name of the network interface.
            duplex (Duplex): The desired duplex mode to set for the interface (e.g., Duplex.DUPLEX_AUTO).

        Returns:
            bool: STATUS_OK if the duplex mode is successfully set, STATUS_NOK otherwise.
        """
        if duplex is Duplex.AUTO:
            self.log.debug(f"do_duplex() - duplex set to auto")
            cmd = ['ethtool', '-s', interface_name, 'autoneg' , 'on']
        else:
            cmd = ['ethtool', '-s', interface_name, 'duplex', duplex.value]

        status = self.run(cmd).exit_code

        if status == STATUS_OK:
            self.log.debug(f"Set duplex mode of {interface_name} to {duplex.name}")
            return STATUS_OK
        else:
            self.log.error(f"Failed to set duplex mode of {interface_name} to {duplex.name}")
            return STATUS_NOK

    def set_speed(self, interface_name: str, ifSpeed: Speed, auto: bool = False) -> bool:
        """
        Set the speed of a network interface and optionally enable or disable auto-negotiation.

        Args:
            interface_name (str): The name of the network interface.
            ifSpeed (Speed): The desired speed to set for the interface.
            autoneg (bool, optional): Whether to enable (True) or disable (False) auto-negotiation. Defaults to False.

        Returns:
            bool: STATUS_OK if the speed is successfully set, STATUS_NOK otherwise.
        """
        try:
            cmd_auto = ['ethtool', '-s', interface_name, 'autoneg', 'on' if auto else 'off']
            status_auto = self.run(cmd_auto).exit_code

            if not auto:
                cmd_speed = ["ethtool", "-s", interface_name, "speed", str(ifSpeed.value)]
                status_speed = self.run(cmd_speed).exit_code

                if status_speed == STATUS_OK:
                    self.log.debug(f"Set speed of {interface_name} to {ifSpeed.name}")
                else:
                    self.log.error(f"Failed to set speed of {interface_name} to {ifSpeed.name}")
            else:
                status_speed = STATUS_OK

            if status_auto == STATUS_OK:
                if auto:
                    self.log.debug(f"Enabled auto-negotiation on {interface_name}")
                else:
                    self.log.debug(f"Disabled auto-negotiation on {interface_name}")
            else:
                self.log.error(f"Failed to set auto-negotiation on {interface_name} to {'on' if auto else 'off'}")

            return status_speed == STATUS_OK and status_auto == STATUS_OK

        except Exception as e:
            self.log.error(f"An error occurred while setting interface speed: {e}")
            return STATUS_NOK

    def set_interface_shutdown(self, interface_name: str, state: State) -> bool:
        """
        Set the state of a network interface (up or down).

        Args:
            interface_name (str): The name of the network interface to configure.
            state (State): The state to set. Valid values are State.UP (to bring the interface up)
                        or State.DOWN (to shut the interface down).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        
        self.log.debug(f"set_interface_state() -> interface_name: {interface_name} -> state: {state}")
        
        if state not in (State.UP, State.DOWN):
            self.log.error("Invalid state. Use State.UP or State.DOWN.")
            return STATUS_NOK

        cmd = ['ip', 'link', 'set', 'dev', interface_name, state.value]

        status = self.run(cmd).exit_code

        if not status:
            self.log.debug(f"Changed state of {interface_name} to {state.value}")
        else:
            self.log.error(f"Failed to change state of {interface_name} to {state.value}")

        return status == STATUS_OK


    
    def set_mtu(self, interface_name: str, mtu_size: int) -> bool:
        """
        Set the Maximum Transmission Unit (MTU) size for a network interface using iproute2.

        Args:
            interface_name (str): The name of the network interface to configure.
            mtu_size (int): The MTU size to set for the interface.

        Returns:
            bool: True if the MTU size was unsuccessfully set, False otherwise.

        """
        # Run the iproute2 command to set the MTU size
        if self.run(['ip', 'link', 'set', interface_name, 'mtu', str(mtu_size)]).exit_code:
            return STATUS_NOK
        else:
            return STATUS_OK
    

        
