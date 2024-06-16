
import logging
from typing import Dict, List
from lib.common.common import Common
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.network_manager.interface import Interface
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class InvalidNetInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class CreateLoopBackNetInterface:
    def __init__(self, loopback_name: str):
        """
        Initialize a CreateLoopBackNetInterface instance to create a loopback network interface.

        Args:
            loopback_name (str): The name of the loopback network interface.

        Raises:
            InvalidNetInterface: If the loopback interface already exists or if creation fails.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS.CREATE_LB_INTERFACE)
        self.loopback_name = loopback_name
        self.interface = Interface()
        self.log.debug(f'Loopback-Name: {loopback_name}')
        
        if Interface().does_os_interface_exist(loopback_name):
            self.log.debug(f'Loopback: {loopback_name} exists')

            if not Interface().db_lookup_interface_exists(loopback_name):
                self.log.debug(f'Loopback: {loopback_name} does not exist in DB...adding')
                Interface().update_interface_db_from_os(loopback_name)
        
        elif not Interface().create_os_loopback(loopback_name):
            self.log.debug(f'Loopback: {loopback_name} didn not exist on OS...Added to OS')
            
            if Interface().add_db_interface_entry(interface_name=loopback_name, ifType=InterfaceType.LOOPBACK):
                raise InvalidNetInterface(f"Unable to add {loopback_name} interface db entry.")
        
        else:
            raise InvalidNetInterface(f"Unable to create {loopback_name} interface.")
                
        self._net_interface = NetInterfaceFactory(self.loopback_name).getNetInterface()
    
    def getNetworkInterface(self) -> 'NetInterface':
        """
        Get a NetInterfaceFactory instance for the created loopback network interface.

        Returns:
            NetInterface: A NetInterface object associated with the created loopback interface.
        """
        self.log.debug(f'getNetworkInterface() -> Interface: {self._net_interface.get_ifType()}')
        return self._net_interface

class NetInterfaceFactory:
    _interface_name_dict: Dict[str, 'NetInterface'] = {}

    def __init__(self, interface_name: str):
        """
        Initialize a NetInterfaceFactory instance with a specific interface name.

        Args:
            interface_name (str): The name of the network interface.
        
        Raises:
            InvalidNetInterface: If the interface is not found in the OS or if it's an invalid loopback format.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS.NET_INTERFACE_FACTORY)
        self.interface_name = interface_name
        
        if self.interface_name in NetInterfaceFactory._interface_name_dict:
            self.log.debug(f'Already created NetInterface Object for interface: {self.interface_name}')
        
        else:
            if not Interface().does_os_interface_exist(interface_name):
                if Common.is_loopback_if_name_valid(interface_name):
                    if Interface().create_os_loopback(interface_name):
                        self.log.debug(f"Created loopback interface: {interface_name}")
                else:
                    raise InvalidNetInterface(f"Invalid loopback interface name format: {interface_name}")
            
            NetInterfaceFactory._interface_name_dict[self.interface_name] = NetInterface(self.interface_name)

    def getNetInterface(self) -> 'NetInterface':
        """
        Retrieve the NetInterface object associated with the specified interface name.

        Returns:
            NetInterface: The NetInterface object for the specified interface name.
        """
        return NetInterfaceFactory._interface_name_dict[self.interface_name]
    
    @staticmethod
    def getNetInterfaceList(interface_name: str) -> 'NetInterface':
        """
        Retrieve the NetInterface object associated with the specified interface name.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            NetInterface: The NetInterface object for the specified interface name.
        """
        return NetInterfaceFactory._interface_name_dict[interface_name]


class NetInterface:
    def __init__(self, interface_name: str):
        """
        Initialize an InterfaceFactory instance with a specific interface name and type.

        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().NET_INTERFACE)        
        self.interface_name = interface_name
        
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
    
    def flush_interface(self) -> bool:
        """
        Flush network interface, removing any configurations.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        return Interface().flush_interface(self.interface_name)

    def get_interface_shutdown_state(self) -> State:
        """
        Get the shutdown state of the network interface.

        Returns:
            State: The current shutdown state of the interface.
        """
        state = Interface().get_os_interface_hardware_info(self.interface_name).get('state')
        return State[state.upper()] if state else None

    def set_interface_shutdown_state(self, state: State) -> bool:
        """
        Set the shutdown state of the network interface.

        Args:
            state (State): The desired shutdown state (UP or DOWN).

        Returns:
            bool: STATUS_OK if the state change is successful, STATUS_NOK otherwise.
        """
        return Interface().update_shutdown(self.interface_name, state)

    def get_interface_speed(self) -> Speed:
        """
        Get the speed of the network interface.

        Returns:
            Speed: The current speed of the interface.
        """
        speed = Interface().get_os_interface_hardware_info(self.interface_name).get('speed')
        return Speed[speed.upper()] if speed else Speed.NONE

    def set_interface_speed(self, speed: Speed) -> bool:
        """
        Set the speed of the network interface.

        Args:
            speed (Speed): The desired speed of the interface.

        Returns:
            bool: STATUS_OK if the speed change is successful, STATUS_NOK otherwise.
        """
        return Interface().update_interface_speed(self.interface_name, speed.value)
    
    def set_proxy_arp(self, negate: bool = False) -> bool:
        """
        Enable or disable Proxy ARP on the network interface.

        This method allows you to enable or disable Proxy ARP on the specified network interface.

        Args:
            negate (bool): If True, Proxy ARP will be disabled. If False, Proxy ARP will be enabled.

        Returns:
            bool: STATUS_OK if the Proxy ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        return Interface().update_interface_proxy_arp(self.interface_name, negate)
    
    def set_drop_gratuitous_arp(self, negate :bool = False) -> bool:
        
        if Interface().update_interface_drop_gratuitous_arp(self.interface_name, (not negate)):
            self.log.error(f'Unable to update_interface_drop_gratuitous_arp for interface: {self.interface_name} ')
            return STATUS_NOK
        
        if Interface().update_db_drop_gratuitous_arp(self.interface_name, (not negate)):
            self.log.error(f'Unable to update_db_drop_gratuitous_arp for interface: {self.interface_name}')
            return STATUS_NOK
        
        return STATUS_OK
        
    def set_mac_address(self, mac_addr: str = None) -> bool:
        """
        Set the MAC address of the network interface.

        If `mac_addr` is None, the interface is set to auto, which typically resets the MAC address to the default hardware address.

        Args:
            mac_addr (str, optional): The new MAC address to assign to the network interface. If None, the MAC address is reset to the default.

        Returns:
            bool: STATUS_OK if the MAC address is successfully updated, STATUS_NOK otherwise.
        """
        return Interface().update_interface_mac(self.interface_name, mac_addr)
    
    def set_duplex(self, duplex: Duplex) -> bool:
        return STATUS_OK
    
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
        return Interface().update_interface_inet(self.interface_name, inet_address, secondary_address, negate)
    
    def add_static_arp(self, inet_address:str, mac_addr:str, negate: bool=False) -> bool:
        return STATUS_OK

