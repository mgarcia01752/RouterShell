import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.network_interfaces.bridge.bridge_group_interface_abc import BridgeGroup
from lib.network_manager.network_interfaces.vlan.vlan_switchport_interface_abc import VlanSwitchport
from lib.network_manager.network_operations.arp import Encapsulate
from lib.network_manager.network_operations.dhcp.client.dhcp_clinet_interface_abc import DHCPInterfaceClient
from lib.network_manager.network_operations.interface import Interface
from lib.network_manager.network_operations.nat import NATDirection

class EthernetInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class EthernetInterface(BridgeGroup, DHCPInterfaceClient, VlanSwitchport):

    def __init__(self, ethernet_name: str):
        BridgeGroup.__init__(self, ethernet_name)
        DHCPInterfaceClient.__init__(self, ethernet_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_INTERFACE)        
        self._interface_name = ethernet_name
    
    def get_interface_name(self) -> str:
        return self._interface_name
            
    def flush_interface(self) -> bool:
        """
        Flush network interface, removing any configurations.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        return Interface().flush_interface(self._interface_name)

    def get_interface_shutdown_state(self) -> State:
        """
        Get the shutdown state of the network interface.

        Returns:
            State: The current shutdown state of the interface.
        """
        state = Interface().get_os_interface_hardware_info(self._interface_name).get('state')
        return State[state.upper()] if state else None

    def set_interface_shutdown_state(self, state: State) -> bool:
        """
        Set the shutdown state of the network interface.

        Args:
            state (State): The desired shutdown state (UP or DOWN).

        Returns:
            bool: STATUS_OK if the state change is successful, STATUS_NOK otherwise.
        """
        return Interface().update_shutdown(self._interface_name, state)

    def get_interface_speed(self) -> Speed:
        """
        Get the speed of the network interface.

        Returns:
            Speed: The current speed of the interface.
        """
        speed = Interface().get_os_interface_hardware_info(self._interface_name).get('speed')
        return Speed[speed.upper()] if speed else Speed.NONE

    def set_interface_speed(self, speed: Speed) -> bool:
        """
        Set the speed of the network interface.

        Args:
            speed (Speed): The desired speed of the interface.

        Returns:
            bool: STATUS_OK if the speed change is successful, STATUS_NOK otherwise.
        """
        return Interface().update_interface_speed(self._interface_name, speed)
    
    def set_proxy_arp(self, negate: bool = False) -> bool:
        """
        Enable or disable Proxy ARP on the network interface.

        This method allows you to enable or disable Proxy ARP on the specified network interface.

        Args:
            negate (bool): If True, Proxy ARP will be disabled. If False, Proxy ARP will be enabled.

        Returns:
            bool: STATUS_OK if the Proxy ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        return Interface().update_interface_proxy_arp(self._interface_name, negate)
    
    def set_drop_gratuitous_arp(self, negate: bool = False) -> bool:
        """
        Sets the drop gratuitous ARP configuration for the interface.

        Args:
            negate (bool, optional): If True, disables dropping gratuitous ARP packets (default: False).

        Returns:
            bool: True if the drop gratuitous ARP configuration was successfully set,
                False otherwise.
        """
        if Interface().update_interface_drop_gratuitous_arp(self._interface_name, (not negate)):
            self.log.error(f'Failed to update drop gratuitous ARP setting for interface: {self._interface_name}')
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
        return Interface().update_interface_mac(self._interface_name, mac_addr)
    
    def set_duplex(self, duplex: Duplex) -> bool:
        """
        Sets the duplex mode for the interface and updates the database entry.

        Args:
            duplex (Duplex): The duplex mode to set for the interface.

        Returns:
            bool: True if the duplex mode was successfully set and updated in the database,
                False otherwise.
        """
        return Interface().update_interface_duplex(self._interface_name, duplex)
    
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
        return Interface().update_interface_inet(self._interface_name, inet_address, secondary_address, negate)
    
    def add_static_arp(self, inet_address: str, mac_addr: str, negate: bool = False) -> bool:
        """
        Adds or removes a static ARP entry for the interface.

        Args:
            inet_address (str): The IP address for the ARP entry.
            mac_addr (str): The MAC address associated with the IP address.
            negate (bool, optional): If True, removes the static ARP entry (default: False).

        Returns:
            bool: True if the static ARP entry was successfully added or removed,
                False otherwise.
        """
        return Interface().update_interface_static_arp(self._interface_name, inet_address, mac_addr, Encapsulate.ARPA, negate)
    
    def get_ifType(self) -> InterfaceType:
        return InterfaceType.ETHERNET
        
    
    def set_nat_domain_direction(self, nat_pool_name: str, nat_direction: NATDirection, negate: bool = False) -> bool:
        """
        Set the NAT domain direction on the specified NAT pool.

        Args:
            nat_pool_name (str): The name of the NAT pool.
            nat_direction (NATDirection): The direction of NAT (inside or outside).
            negate (bool): If True, remove the NAT direction; otherwise, set the NAT direction.

        Returns:
            bool: STATUS_OK if the NAT direction was successfully set, STATUS_NOK otherwise.
        """
        if Interface.set_nat_domain_status(self, self._interface_name, nat_pool_name, nat_direction, negate):
            self.log.error(f'Unable to add NAT-{nat_direction.name} to pool-name: {nat_pool_name} Negate: {negate}')
            return STATUS_NOK
        return STATUS_OK

