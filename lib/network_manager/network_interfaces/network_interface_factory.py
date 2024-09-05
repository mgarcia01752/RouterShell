import logging
from typing import Dict, Union

from lib.network_manager.common.interface import InterfaceType
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.network_interfaces.ethernet.ethernet_interface import EthernetInterface
from lib.network_manager.network_interfaces.loopback_interface import LoopbackInterface
from lib.network_manager.network_interfaces.wireless_wifi_interface import WirelessWifiInterface
   
class NetInterfaceFactoryError(Exception):
    def __init__(self, message):
        super().__init__(message)

class NetInterfaceFactory:
    """
    Factory class for creating and managing network interfaces.

    This class provides a factory mechanism for creating instances of different types of network interfaces such as
    loopback, Ethernet, and wireless interfaces. It ensures that only one instance of a particular interface is created
    and reused if requested again.

    Attributes:
        interface_name (str): The name of the network interface.
        log (logging.Logger): Logger for logging operations.

    Raises:
        NetInterfaceFactoryError: If required arguments are missing or invalid, or if the interface type is unsupported.
    """

    # Singleton {'interface_name': NetworkInterface}
    _net_interface_lookup_interface_name: Dict[str, Union[LoopbackInterface, EthernetInterface, WirelessWifiInterface]] = {}

    def __init__(self, interface_name: str, interface_type: InterfaceType):
        """
        Initializes the NetInterfaceFactory with the given interface name and type.

        Args:
            interface_name (str): The name of the network interface.
            interface_type (InterfaceType): The type of the network interface (e.g., LOOPBACK, ETHERNET, WIRELESS_WIFI).

        Raises:
            NetInterfaceFactoryError: If required arguments are missing or invalid, or if the interface type is unsupported.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS.NET_INTERFACE_FACTORY)
        self.interface_name = interface_name
        
        if not interface_name or not interface_type:
            raise NetInterfaceFactoryError('Arguments missing')
        
        if self.interface_name in NetInterfaceFactory._net_interface_lookup_interface_name:
            self.log.debug(f'Already created NetInterface Object for interface: {self.interface_name}')
        
        else:
            
            if interface_type == InterfaceType.LOOPBACK:
                network_interface_obj = LoopbackInterface(self.interface_name)
                
            elif interface_type == InterfaceType.ETHERNET:
                network_interface_obj = EthernetInterface(self.interface_name)
            
            elif interface_type == InterfaceType.WIRELESS_WIFI:
                network_interface_obj = WirelessWifiInterface(self.interface_name)
            
            else:
                raise NetInterfaceFactoryError(f"Unsupported interface type: {interface_type}")

            NetInterfaceFactory._net_interface_lookup_interface_name[self.interface_name] = network_interface_obj
            
    def getNetInterface(self) -> Union[LoopbackInterface, EthernetInterface, WirelessWifiInterface]:
        """
        Retrieve the NetworkInterface object associated with the specified interface name.

        Returns:
            Union[LoopbackInterface, EthernetInterface, WirelessWifiInterface]: The NetworkInterface object for the specified interface.
        """
        return NetInterfaceFactory._net_interface_lookup_interface_name[self.interface_name]
    
    @staticmethod
    def getNetInterface(interface_name: str) -> Union[LoopbackInterface, EthernetInterface, WirelessWifiInterface]:
        """
        Retrieve the NetInterface object associated with the specified interface name.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            NetworkInterface (Base Object Class): The NetworkInterface object for the specified interface name.
        """
        return NetInterfaceFactory._net_interface_lookup_interface_name.get(interface_name)