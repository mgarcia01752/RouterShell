from enum import Enum
import re
import logging

from lib.network_manager.common.phy import PhyServiceLayer
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.common.constants import STATUS_NOK, STATUS_OK

class InterfaceLayerFoundError(Exception):

    def __init__(self, message="Interface Layer error"):
        self.message = message
        super().__init__(self.message)

class InterfaceType(Enum):
    """
    Enumeration representing different types of network interfaces.

    Each member of the enumeration corresponds to a specific type of network interface.
    The values are used to identify and categorize network interfaces based on their characteristics.

    Enum Members:
        DEFAULT (str): Default type.
        PHYSICAL (str): Physical interface type.
        ETHERNET (str): Ethernet interface type.
        VLAN (str): Virtual LAN interface type.
        LOOPBACK (str): Loopback interface type.
        VIRTUAL (str): Virtual interface type.
        BRIDGE (str): Bridge interface type.
        WIRELESS_WIFI (str): Wireless Wi-Fi interface type.
        WIRELESS_CELL (str): Wireless cellular interface type.
        UNKNOWN (str): Unknown or undefined interface type.
    """
    DEFAULT = 'if' 
    PHYSICAL = 'phy'
    ETHERNET = 'eth'
    VLAN = 'vlan'
    LOOPBACK = 'loopback'
    VIRTUAL = 'vir'
    BRIDGE = 'br'
    WIRELESS_WIFI = 'wifi'
    WIRELESS_CELL = 'cell'
    UNKNOWN = 'UNKNOWN'

class InterfaceLayer(PhyServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INTERFACE)
        
    def get_os_interface_type(self, interface_name: str) -> InterfaceType:
        """
        Determines the type of a network interface using information from the 'nmcli dev show' command.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            InterfaceType: An enumeration representing the type of the network interface.
            Returns InterfaceType.UNKNOWN if an error occurs or if the interface type is unknown.

        Raises:
            InterfaceLayerFoundError: If an error occurs during the execution of 'nmcli dev show'.
        """
        try:
            output = self.run(["nmcli", "dev", "show", interface_name])

            if output.exit_code:
                self.log.error(f"Error executing 'nmcli': {output.stderr}")
                return InterfaceType.UNKNOWN

            if re.search(r"\bGENERAL\.TYPE:\s*wifi\b", output.stdout):
                return InterfaceType.WIRELESS_WIFI

            elif re.search(r"\bGENERAL\.TYPE:\s*gsm\b", output.stdout):
                return InterfaceType.WIRELESS_CELL

            elif re.search(r"\bGENERAL\.TYPE:\s*ethernet\b", output.stdout):
                return InterfaceType.ETHERNET

            elif re.search(r"\bGENERAL\.TYPE:\s*vlan\b", output.stdout):
                return InterfaceType.VLAN

            elif re.search(r"\bGENERAL\.TYPE:\s*bridge\b", output.stdout):
                return InterfaceType.BRIDGE

            elif re.search(r"\bGENERAL\.TYPE:\s*tun\b", output.stdout):
                return InterfaceType.VIRTUAL

            elif re.search(r"\bGENERAL\.TYPE:\s*loopback\b", output.stdout):
                return InterfaceType.LOOPBACK

            else:
                return InterfaceType.UNKNOWN

        except InterfaceLayerFoundError as e:
            self.log.error(f"An error occurred: {e}")
            return InterfaceType.UNKNOWN


            

        