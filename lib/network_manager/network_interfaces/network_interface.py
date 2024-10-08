
import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import State
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.network_operations.interface import Interface

class NetworkInterface:
    """
    Base class for all network interfaces.

    This class serves as a parent class for specific types of network interfaces like loopback, Ethernet, and wireless interfaces.
    It provides a common interface name attribute and a logger for logging operations.

    Attributes:
        interface_name (str): The name of the network interface.
        log (logging.Logger): Logger for logging operations.
    """

    def __init__(self, interface_name: str) -> None:
        """
        Initializes the NetworkInterface with the given interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS.NETWORK_INTERFACE)
        self.interface_name = interface_name
        pass

    def set_description(self, description:str=None) -> bool:
        """
        Set the description for the network interface.

        Args:
            description (str, optional): The description to set for the network interface. Defaults to None.

        Returns:
            bool: True if the description is successfully updated, False otherwise (STATUS_NOK).
        """
        if Interface().update_db_description(self.interface_name, description):
            return STATUS_NOK
        
        return STATUS_OK

    def get_ifType(self) -> InterfaceType:
        """
        Retrieve the type of the network interface.

        Returns:
            InterfaceType: The type of the network interface.
        """
        return Interface().get_os_interface_type_extened(self.interface_name)

    def get_interface_name(self) -> str:
        """
        Retrieve the name of the network interface.

        Returns:
            str: The name of the network interface.
        """
        return self.interface_name

    def interface_exist_os(self) -> bool:
        """
        Check if the network interface exists in the operating system.

        This method verifies the existence of the network interface specified by `interface_name` in the operating system.

        Returns:
            bool: True if the interface exists, False otherwise.
        """
        return Interface().does_os_interface_exist(self.interface_name)

    def interface_exist_db(self) -> bool:
        """
        Check if the network interface exists in the database.

        Returns:
            bool: True if the interface exists in the database, False otherwise.
        """
        if self.interface_name in Interface().get_db_interface_names():
            return True
        return False

    def get_interface_shutdown_state(self) -> State:
        """
        Get the shutdown state of the network interface.

        Returns:
            State: The current shutdown state of the interface.
        """
        pass

    def set_interface_shutdown_state(self, state: State) -> bool:
        """
        Set the shutdown state of the network interface.

        Args:
            state (State): The desired shutdown state (UP or DOWN).

        Returns:
            bool: STATUS_OK if the state change is successful, STATUS_NOK otherwise.
        """
        pass
    
    def set_mac_address(self, mac_addr: str = None) -> bool:
        """
        Set the MAC address of the network interface.

        If `mac_addr` is None, the interface is set to auto, which typically resets the MAC address to the default hardware address.

        Args:
            mac_addr (str, optional): The new MAC address to assign to the network interface. If None, the MAC address is reset to the default.

        Returns:
            bool: STATUS_OK if the MAC address is successfully updated, STATUS_NOK otherwise.
        """
        pass
    
    def add_inet_address(self, inet_address, secondary_address:bool=False, negate:bool=False) -> bool:
        """
        Add or modify an IP address on the network interface.

        Args:
            inet_address (str): The IP address to add or modify.
            secondary_address (bool, optional): Whether the IP address is a secondary address. Defaults to False.
            negate (bool, optional): Whether to remove the IP address if it exists. Defaults to False.

        Returns:
            bool: True if the IP address is successfully added or modified, False otherwise.
        """
        pass