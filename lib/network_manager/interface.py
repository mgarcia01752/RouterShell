import ipaddress
import json
import logging
import re
from typing import List, Optional, Union

from lib.db.interface_db import InterfaceDatabase
from lib.network_manager.arp import Arp, Encapsulate

from lib.network_manager.bridge import Bridge, BridgeProtocol as BrProc
from lib.network_manager.dhcp_client import DHCPClient, DHCPVersion
from lib.network_manager.network_mgr import NetworkManager
from lib.network_manager.vlan import Vlan
from lib.network_manager.common.interface import InterfaceType 
from lib.network_manager.nat import Nat, NATDirection
from lib.network_manager.common.phy import Duplex, Speed, State

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK

class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class Interface(NetworkManager, InterfaceDatabase):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INTERFACE)
        self.arg = arg

    def clear_interface_arp(self, interface_name: str = None) -> bool:
        """
        Clear the ARP cache for a specific network interface using iproute2.

        This method clears the ARP cache for the specified network interface using the iproute2 tool.

        Args:
            interface_name (str, optional): The name of the network interface to clear the ARP cache for.
                If not provided, the ARP cache for all interfaces will be cleared. Defaults to None.

        Returns:
            bool: STATUS_OK if the ARP cache was successfully cleared, STATUS_NOK otherwise.
        """

        if interface_name:
            # Clear the ARP cache for a specific interface
            self.run(['sudo', 'ip', 'neigh', 'flush', 'dev', interface_name], suppress_error=True)
        else:
            # Clear the ARP cache for all interfaces
            self.run(['sudo', 'ip', 'neigh', 'flush', 'all'], suppress_error=True)
        return STATUS_OK

    def get_network_interfaces(self) -> list:
        """
        Get a list of network interface names (excluding bridges) using the 'ip' command with --json option.

        Returns:
            List[str]: A list of network interface names.
        """
        result = self.run(['ip', '-json', 'link', 'show'])

        if result.exit_code:
            return []

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                interfaces = data.get("link", [])
            elif isinstance(data, list):
                interfaces = data
            else:
                print("Unexpected JSON format")
                return []

            # Filter out interfaces based on your criteria (e.g., excluding bridges)
            interface_list = [iface["ifname"] for iface in interfaces if "BROADCAST,MULTICAST" not in iface.get("flags", [])]
            return interface_list
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []

    def get_interface_type_via_iproute(self, interface_name:str) -> InterfaceType:
        """
            Get the type of a network interface (physical, virtual, or VLAN) based on its name.

            Args:
                interface_name (str): The name of the network interface to query.

            Returns:
                str: The type of the interface, which can be 'Physical', 'Virtual', 'VLAN', or 'Unknown'.
                    Returns 'None' if the interface is not found.
        """

        result = self.run(['ip', 'link', 'show' , interface_name], suppress_error=True)
        self.log.debug(f"get_interface_type() -> sdtout: {result.stdout}")
        
        if result.exit_code:
            self.log.debug(f"get_interface_type() -> Interface Not Found: {interface_name}")
            return InterfaceType.UNKNOWN
        
        # Split the output into lines
        lines = result.stdout.split('\n')
        
        for line in lines:
            self.log.debug(f"Line {line}")

            if 'link/ether' in line:
                return InterfaceType.ETHERNET

            elif 'link/tun' in line or 'link/tap' in line:
                return InterfaceType.VIRTUAL

            elif 'vlan' in line:
                return InterfaceType.VLAN

            elif 'bridge' in line:
                return InterfaceType.BRIDGE

            elif 'link/loopback' in line:
                return InterfaceType.LOOPBACK
            
        return InterfaceType.UNKNOWN

    def get_interface_type(self, interface_name: str) -> InterfaceType:
        """
        Get the type of a network interface using lshw.

        This method retrieves information about the network interface using lshw and determines its type based on the
        capabilities and configuration.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            InterfaceType: An enumeration representing the type of the network interface.
        """
        interface_info = self.get_interface_info(interface_name)
        
        if not interface_info:
            if_type =  self.get_interface_type_via_iproute(interface_name)
            return if_type
        
        elif interface_info.get('capabilities', {}).get('wireless'):
            return InterfaceType.WIRELESS_WIFI
        
        elif interface_info.get('capabilities', {}).get('tp'):
            return InterfaceType.ETHERNET
        
        elif interface_info.get('configuration', {}).get('duplex'):
            return InterfaceType.ETHERNET
        
        return self.get_interface_type_via_iproute(interface_name)

    def get_interface_type_via_db(self, interface_name) -> InterfaceType:
        """
        Get the interface type for a specified interface name from the database.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            InterfaceType: The type of the interface.
        """
        interface_details = self.get_interface_details()

        for if_dict in interface_details:
            if if_dict['Interfaces']['InterfaceName'] == interface_name:                
                interface_type_str = if_dict['Interfaces']['Properties']['InterfaceType']
                for interface_enum in InterfaceType:
                    if interface_type_str == interface_enum.value:
                        return interface_enum

        return InterfaceType.UNKNOWN

    def does_interface_exist(self, interface_name: str) -> bool:
        """
        Determine if a network interface with the specified name exists on the current system.

        This method utilizes the 'ip link' command to retrieve a list of all network interfaces
        present on the system and subsequently verifies if the provided interface name is
        included in the command's output.

        Args:
            interface_name (str): The name of the network interface to be checked.

        Returns:
            bool: A boolean value indicating the existence of the specified interface.
            - True: The interface exists.
            - False: otherwise
        """
        try:
            result = self.run(['ip', 'link', 'show', interface_name], suppress_error=True)

            if result.exit_code:
                self.log.debug(f"does_interface_exist() return a non-zero: {result.exit_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log.error(f"{e}")
            return False

    def add_interface_entry(self, interface_name: str, ifType: InterfaceType) -> bool:
        """
        Add an interface entry to the database.

        Args:
            interface_name (str): The name of the interface to be added.
            ifType (InterfaceType): The type of the interface.

        Returns:
            bool: STATUS_OK if the interface entry is added successfully, STATUS_NOK if there is an error.

        """
        if self.add_db_interface(interface_name, ifType):
            self.log.debug(f"Unable to add interface: {interface_name} to DB")
            return STATUS_NOK
        
        if ifType != InterfaceType.ETHERNET:
            self.update_db_ifSpeed(interface_name, None)
            self.update_db_duplex(interface_name, None)
        
        return STATUS_OK
        
    def update_interface_mac(self, interface_name: str, mac: Optional[str] = None) -> bool:
        """
        Update the MAC address of a network interface.
        Update the MAC address to the DB 

        This method either generates a random MAC address or uses the provided MAC address
        (if valid) and assigns it to the specified network interface.

        Args:
        
        interface_name (str): The name of the network interface to which the MAC address will be assigned.
        
        mac (str, optional): Supported MAC address formats:
        - xx:xx:xx:xx:xx:xx
        - xx-xx-xx-xx-xx-xx
        - xxxx.xxxx.xxxx
        - xxxxxxxxxxxx

        Returns:
            bool: STATUS_OK if the MAC address was successfully added, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_interface_mac() -> interface_name: {interface_name} -> mac: {mac}")

        if not mac:
            new_mac = self.generate_random_mac()
            self.log.debug(f"update_interface_mac() mac-auto: {new_mac}")

        elif self.is_valid_mac_address(mac):
            stat, format_mac = self.format_mac_address(mac)
            self.log.debug(f"update_interface_mac() -> mac: {mac} -> format_mac: {format_mac}")

            if not stat:
                self.log.error(f"Unable to format MAC address: {mac}")
                return STATUS_NOK

        else:
            self.log.error(f"Invalid MAC address: {mac}")
            return STATUS_NOK

        if self.set_interface_mac(interface_name, new_mac if not mac else format_mac):
            self.log.error(f"Unable to set MAC address to interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_mac_address(interface_name, new_mac if not mac else format_mac):
            self.log.error(f"Unable to set MAC address to interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_inet(self, interface_name: str, inet_address: str, secondary: bool = False, negate: bool = False) -> bool:
        """
        Add or remove an inet address from a network interface.
        Update interface inet DB
        
        This method either adds or removes an inet address from the specified network interface.

        Args:
            interface_name (str): The name of the network interface.
            inet_address (str): The IP address in CIDR notation (e.g., "192.168.1.1/24" for IPv4 or "2001:db8::1/64" for IPv6).
            secondary (bool, optional): If True, the method will configure the address as secondary. If False, it will configure it as the primary address (default is False).
            negate (bool): If True, the method will remove the specified IP address from the interface. If False, it will add the address.

        Returns:
            bool: STATUS_OK if the IP address was successfully updated, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_interface_inet() -> interface: {interface_name} -> inet: {inet_address} -> secondary: {secondary} -> negate: {negate}")

        if negate:
            if self.del_inet_address(interface_name, inet_address):
                self.log.error(f"Unable to remove inet Address: {inet_address} from interface: {interface_name} via OS")
                return STATUS_NOK
            
        else:
            if self.set_inet_address(interface_name, inet_address, secondary):
                self.log.error(f"Unable to set inet Address: {inet_address} to interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_db_inet_address(interface_name, inet_address, secondary, negate):
            self.log.error(f"Unable to update inet Address: {inet_address} to interface: {interface_name} via DB")
            return STATUS_NOK
        
        return STATUS_OK

    def update_interface_duplex(self, interface_name: str, duplex: Duplex) -> bool:
        """
        Add or set the duplex mode for a network interface.

        This method allows adding or setting the duplex mode to 'auto', 'half', or 'full' for the specified interface.

        Args:
            interface_name (str): The name of the network interface to configure.
            duplex (Duplex): The duplex mode to set. Valid values are Duplex.AUTO, Duplex.HALF, or Duplex.FULL.

        Returns:
            bool: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        
        if duplex == Duplex.NONE:
            
            if self.update_db_duplex(interface_name, duplex.value):
                self.log.error(f"Unable to update interface: {interface_name} to duplex: {duplex.value}")
                return STATUS_NOK
            
            return STATUS_OK            
        
        if self.set_duplex(interface_name, duplex):
            print(f"Invalid duplex mode ({duplex.value}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
        
        if self.update_db_duplex(interface_name, duplex.value):
            self.log.error(f"Unable to update interface: {interface_name} to duplex: {duplex.value}")
            return STATUS_NOK
            
        self.log.debug(f"Updated interface: {interface_name} to duplex: {duplex.value}")
        
        return STATUS_OK
    
    def update_interface_speed(self, interface_name: str, speed: Speed) -> bool:
        """
        Set the network interface speed and update it in the database.

        Args:
            interface_name (str): The name of the network interface to configure.
            speed (Speed): The desired speed setting.

        Returns:
            bool: STATUS_OK if the speed configuration was successful, STATUS_NOK otherwise.
        """

        self.log.debug(f"update_interface_speed() -> interface: {interface_name} Speed: {speed}")
        
        if speed == Speed.NONE:
            if self.update_db_ifSpeed(interface_name, speed.value):
                return STATUS_NOK
            return STATUS_OK
        
        if speed == Speed.AUTO_NEGOTIATE:
            self.set_speed(interface_name, Speed.AUTO_NEGOTIATE, Speed.AUTO_NEGOTIATE)
            self.update_db_ifSpeed(interface_name, Speed.AUTO_NEGOTIATE.value)
            
        elif speed in {Speed.MBPS_10, Speed.MBPS_100, Speed.MBPS_1000, Speed.MBPS_10000}:
            self.set_speed(interface_name, speed)
            self.update_db_ifSpeed(interface_name, speed.value)
        
        else:
            print("Invalid speed value. Use Speed.MBPS_10, Speed.MBPS_100, Speed.MBPS_1000, Speed.MBPS_10000, or Speed.AUTO_NEGOTIATE.")
            return STATUS_NOK
        
        return STATUS_OK
            
    def update_shutdown(self, interface_name: str, state: State) -> bool:
        """
        Set the shutdown status of a network interface.

        This method allows setting the shutdown status of the specified network interface to 'up' or 'down'.

        Args:
            interface_name (str): The name of the network interface to configure.
            state (State): The status to set. Valid values are State.UP (to bring the interface up)
                        or State.DOWN (to shut the interface down).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        shutdown = state != State.UP
        
        if self.update_db_shutdown_status(interface_name, shutdown):
            self.log.error(f"Unable to set interface: {interface_name} to {state.value} via db")
            return STATUS_NOK
        
        self.log.debug(f"update_shutdown() -> interface_name: {interface_name} -> State: {state} via os")
        return self.set_interface_shutdown(interface_name, state)
 
    def update_interface_bridge_group(self, interface_name:str, br_id:str, stp_protocol:BrProc=BrProc.IEEE_802_1D) -> bool:
        """
        Set the bridge group and Spanning Tree Protocol (STP) configuration for a network interface.

        This method allows configuring a network interface to be a part of a specific bridge group with optional STP protocol selection.

        Args:
            interface_name (str): The name of the network interface to configure.
            br_id (str): The identifier of the bridge group to join.
            stp_protocol (BrProc): The STP protocol to use for the bridge group (default is IEEE 802.1D).

        Returns:
            bool: A status string indicating the result of the operation. 'STATUS_OK' if successful,
                 'STATUS_NOK' if the specified bridge group does not exist.

        """
        if Bridge().add_bridge_to_interface(interface_name, br_id, stp_protocol) == STATUS_NOK:
            print(f"bridge-group {br_id} does not exists")
            return STATUS_NOK
        return STATUS_OK
    
    def create_loopback(self, interface_name:str) -> bool:
        """
        Create a loopback interface with the specified name.

        Args:
            interface_name (str): The name for the loopback interface.

        Returns:
            bool: True if the loopback interface was created successfully, False otherwise.
        """
        result = self.run(['ip', 'link', 'add', 'name', interface_name , 'type', 'dummy'], suppress_error=True)
        
        if result.exit_code:
            self.log.error(f'Error creating loopback -> {interface_name}')
            return STATUS_NOK
        
        self.log.debug(f'Created {interface_name} Loopback')
        
        return STATUS_OK
    
    def update_interface_vlan(self, interface_name:str, vlan_id:int=1000) -> bool:
        """
        Update VLAN to a network interface or bridge via os
        Update VLAN to a network interface or bridge via db

        Args:
            interface_name (str): The name of the network interface.
            vlan_id (int, optional): The VLAN ID to assign. Defaults to 1000.

        Returns:
            STATUS_OK if the VLAN assignment was successful, STATUS_NOK is failed
        """
        self.log.debug(f"set_vlan() -> interface_name: {interface_name} vlan_id: {vlan_id}")

        brName = Bridge().get_assigned_bridge_from_interface(interface_name)

        if brName:
            self.log.debug(f"Assigned VLAN: {vlan_id} to Bridge: {brName}")
            return Vlan().add_interface_to_vlan(brName, vlan_id, InterfaceType.BRIDGE)
        
        else:
            self.log.debug(f"Assigned VLAN: {vlan_id} to interface: {interface_name}")
            return Vlan().add_interface_to_vlan(interface_name, vlan_id, InterfaceType.ETHERNET)
    
    def del_interface_vlan(self, vlan_id:int) -> bool:
        """
        Delete a VLAN to a network interface or bridge.

        Args:
            vlan_id (int): The VLAN ID to assign.

        Returns:
            STATUS_OK if the VLAN assignment was successful, STATUS_NOK is failed
        """
        self.log.debug(f"del_vlan() -> vlan_id: {vlan_id}")

        return Vlan().del_interface_to_vlan(vlan_id)

    def rename_interface(self, initial_interface_name:str, alias_interface_name:str) -> bool:
        """
        Rename a network interface

        Args:
            initial_interface_name (str): The current name of the network interface.
            alias_interface_name (str): The new name to assign to the network interface.

        Returns:
            bool: STATUS_OK if the interface was successfully renamed, STATUS_NOK otherwise.
        """
        self.log.debug(f"rename_interface() -> if: {initial_interface_name} -> alias-if: {alias_interface_name}")
        
        if not self.does_interface_exist(initial_interface_name):
            self.log.error(f"Interface: {initial_interface_name} does not exists")
            return STATUS_NOK        

        bus_info = self.get_interface_info(initial_interface_name)['businfo']
        
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)
                
        if self.db_lookup_interface_alias_exist(initial_interface_name, alias_interface_name):
            self.log.debug(f"Alias-Interface already exists: {alias_interface_name} assigned to initial-interface: {initial_interface_name}")
            return STATUS_OK
        
        if result.exit_code:
            self.log.error(f"Unable to rename interface {initial_interface_name} to {alias_interface_name} to OS")
            return STATUS_NOK
        
        if self.update_db_rename_alias(bus_info, initial_interface_name, alias_interface_name):
            self.log.error(f"Unable to add init-interface: {initial_interface_name} to alias-interface: {alias_interface_name} to DB")
            return STATUS_NOK
        
        return STATUS_OK        

    def update_rename_interface_via_os(self, reverse=False) -> bool:
        """
        Update and rename network interfaces via the operating system.

        This method iterates through the list of interface aliases and uses the '_rename_os_interface' method
        to update and rename each network interface via the operating system.

        Args:
            reverse (bool, optional): If True, reverses the renaming process, restoring original names.

        Returns:
            bool: STATUS_OK if the update and rename process is successful for all interfaces, STATUS_NOK otherwise.
        """
        for alias in self.get_interface_aliases():
            original_name = alias['InterfaceName']
            alias_name = alias['AliasInterface']

            self.log.debug(f'orig-interface: {original_name} -> new-interface: {alias_name}')

            if reverse:
                original_name, alias_name = alias_name, original_name

            if self._rename_os_interface(original_name, alias_name):
                self.log.error(f"Failed to update and rename interface: {original_name} to {alias_name}")
                return STATUS_NOK

            self.log.debug(f"Interface {original_name} successfully updated and renamed to {alias_name}")

        return STATUS_OK

    def update_interface_proxy_arp(self, interface_name: str, negate: bool = False) -> bool:
        """
        Enable or disable Proxy ARP on a network interface and update the Proxy ARP configuration in the database.

        This method allows you to enable or disable Proxy ARP on the specified network interface and update the Proxy ARP
        configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            negate (bool): If True, Proxy ARP will be disabled on the interface. If False, Proxy ARP will be enabled.

        Returns:
            bool: STATUS_OK if the Proxy ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        if Arp().set_os_proxy_arp(interface_name, negate):
            self.log.error(f"Unable to update proxy-arp: {not negate} on interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_proxy_arp(interface_name, (not negate)):
            self.log.error(f"Unable to update proxy-arp: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_drop_gratuitous_arp(self, interface_name: str, negate: bool = False) -> bool:
        """
        Enable or disable the dropping of gratuitous ARP packets on a network interface and update the configuration in the database.

        This method allows you to enable or disable the dropping of gratuitous ARP packets on the specified network interface
        and update the configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            negate (bool): If True, gratuitous ARP dropping will be disabled on the interface. If False, it will be enabled.

        Returns:
            bool: STATUS_OK if the gratuitous ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        if Arp().set_os_drop_gratuitous_arp(interface_name, negate):
            self.log.error(f"Unable to update drop-gratuitous-arp: {not negate} on interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_drop_gratuitous_arp(interface_name, (not negate)):
            self.log.error(f"Unable to update drop-gratuitous-arp: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_static_arp(self, interface_name: str, inet: str, mac_address: str, encap: Encapsulate, negate: bool = False) -> bool:
        """
        Enable or disable a static ARP entry for a network interface and update the static ARP configuration in the database.

        This method allows you to enable or disable a static ARP entry on the specified network interface and update the
        static ARP configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            inet (str): The IP address associated with the ARP entry.
            mac_address (str): The MAC address associated with the ARP entry.
            encap (Encapsulate): The type of encapsulation used for the ARP entry.
            negate (bool): If True, the static ARP entry will be disabled. If False, the static ARP entry will be enabled.

        Returns:
            bool: STATUS_OK if the static ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        status, mac_address = self.format_mac_address(mac_address)
        
        if not status:
            self.log.error(f"Invalid ARP entry mac address: {mac_address}")
            return STATUS_NOK
        
        if not Arp().is_arp_entry_exists(inet):
            self.log.debug(f"ARP entry for {inet} already exists")
            
            if Arp().set_os_static_arp(interface_name, inet, mac_address, encap.value, not negate):
                self.log.error(f"Unable to update static ARP: {not negate} on interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_db_static_arp(interface_name, inet, mac_address, encap.value, negate):
            self.log.error(f"Unable to update static ARP: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_dhcp_client(self, interface_name: str, dhcp_version: DHCPVersion, negate=False) -> bool:
        """
        Update the DHCP configuration for a network interface via OS.
        Update the DHCP configuration for a network interface via DB.
        
        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (DHCPVersion): The DHCP version (DHCP_V4 or DHCP_V6).
            negate (bool): If True, disable DHCP; if False, enable DHCP.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.

        """
        dhcp_client = DHCPClient()
        if not dhcp_client.is_dhclient_available:
            self.log.critical(f"DHCP Client Service not available, check system logs")
            return STATUS_NOK
        
        if not self.net_mgr_interface_exist(interface_name):
            self.log.error(f"Unable to update {dhcp_version.value} client on interface: {interface_name}. Interface does not exist.")
            return STATUS_NOK
        
        if self.update_db_dhcp_client(interface_name, dhcp_version):
            self.log.error(f"Failed to update {dhcp_version.value} client on interface: {interface_name}. Database update error.")
            return STATUS_NOK
        
        if dhcp_client.set_dhcp_client_interface_service(interface_name, dhcp_version, (not negate)):
            self.log.error(f"Unable to update {dhcp_version.value} client on interface: {interface_name} OS update error.")
            return STATUS_NOK

        return STATUS_OK            

    def set_nat_domain_status_1(self, interface_name:str, nat_in_out:NATDirection, negate=False):
        
        if nat_in_out is NATDirection.INSIDE:
            if Nat().create_inside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
        else:
            if Nat().create_outside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
            
        return STATUS_OK        

    def set_nat_domain_status_2(self, interface_name:str, nat_pool_name:str, nat_in_out:NATDirection, negate=False):
        if nat_in_out == NATDirection.INSIDE.value:
            self.log.debug("Configuring NAT for the inside interface")
            
            if Nat().create_inside_nat(nat_pool_name, self.ifName, negate):
                self.log.error(f"Unable to set INSIDE NAT to interface: {self.ifName} to NAT-pool {nat_pool_name}")
                return STATUS_NOK

            if self.update_db_nat_direction(self.ifName, nat_pool_name, NATDirection.INSIDE, negate):
                self.log.debug(f"Unable to update NAT Direction: {nat_in_out}")
                return STATUS_NOK
        
        elif nat_in_out == NATDirection.OUTSIDE.value:
            self.log.debug("Configuring NAT for the outside interface")
            
            if Nat().create_outside_nat(nat_pool_name, self.ifName, negate):
                self.log.error(f"Unable to set OUTSIDE NAT to interface: {self.ifName} to NAT-pool {nat_pool_name}")
                return STATUS_NOK
            
            if self.update_db_nat_direction(self.ifName, nat_pool_name, NATDirection.OUTSIDE, negate):
                self.log.debug(f"Unable to update NAT Direction: {nat_in_out}")
                return STATUS_NOK
        return STATUS_OK

    def set_nat_domain_status(self, interface_name: str, nat_pool_name: str, nat_in_out: NATDirection, negate=False) -> bool:
        """
        Configure NAT domain status for an interface.

        Args:
            interface_name (str): The name of the interface.
            nat_pool_name (str): The name of the NAT pool.
            nat_in_out (NATDirection): The direction of NAT (INSIDE or OUTSIDE).
            negate (bool, optional): Whether to negate the NAT configuration. Default is False.

        Returns:
            bool: STATUS_OK if NAT configuration is successful, STATUS_NOK if there is an error.

        """
        if nat_in_out == NATDirection.INSIDE:
            self.log.debug("Configuring NAT for the inside interface")

            if Nat().create_inside_nat(nat_pool_name, interface_name, negate):
                self.log.error(f"Unable to set INSIDE NAT to interface: {interface_name} to NAT-pool {nat_pool_name} via OS")
                return STATUS_NOK
            
        elif nat_in_out == NATDirection.OUTSIDE:
            self.log.debug("Configuring NAT for the outside interface")

            if Nat().create_outside_nat(nat_pool_name, interface_name, negate):
                self.log.error(f"Unable to set OUTSIDE NAT to interface: {interface_name} to NAT-pool {nat_pool_name} via OS")
                return STATUS_NOK

        return STATUS_OK

    def get_interface_info(self, interface_name: str) -> dict:
        """
        Retrieve information about network interfaces using lshw.

        Args:
            interface_name (str): The name of the network interface to retrieve information for.

        Returns:
            dict or None: A dictionary containing information about the network interface if successful,
                          None otherwise.
        """
        try:
            result = self.run(['lshw', '-c', 'network', '-json'], suppress_error=True)

            if result.exit_code == 0:
                output_json = json.loads(result.stdout)

                for interface in output_json:
                    if interface.get('logicalname') == interface_name:
                        return interface

                self.log.debug(f"No information found for interface: {interface_name}")
                return None
            
            else:
                self.log.debug(f"Error running lshw command. Exit code: {result.exit_code}")
                return None

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error decoding JSON: {e}")
            return None

    def update_interface_description(self, interface_name: str, description: str) -> bool:
        """
        Update the description of a network interface in the database.

        This method allows you to update the user-defined description of a specific network interface in the database.

        Args:
            interface_name (str): The name of the network interface.
            description (str): The new description to assign to the network interface.

        Returns:
            bool: STATUS_OK if the description is successfully updated, STATUS_NOK otherwise.
        """
        return self.update_db_description(interface_name, description)

    def update_interface_db_from_os(self, interface_name: str = None) -> bool:
        """
        Update the database with information about network interfaces found by the operating system.

        This method iterates through all network interfaces discovered by the operating system,
        checks the database to ensure that each interface is not already defined. If not defined,
        it creates an entry with basic configuration. Otherwise, it skips the interface.

        Args:
            interface_name (str, optional): The name of a specific network interface to update.

        Returns:
            bool: STATUS_OK if the update process is successful, STATUS_NOK otherwise.
        """
        for if_name in self.get_network_interfaces():
            
            if interface_name is not None and if_name != interface_name or not self.db_lookup_interface_exists(if_name):
                self.log.debug(f"Unknown interface: {if_name}")
                continue
            
            if_type = self.get_interface_type(if_name)
                       
            if if_type != InterfaceType.UNKNOWN:
                self.log.debug(f"Adding Interface: {if_name} -> if-type: {if_type.name} to DB")
                self.add_interface_entry(if_name, if_type)
                self.update_interface_description(if_name,f'Interface Type: {if_type.name}')
                self.update_shutdown(if_name, State.UP)

        return STATUS_OK

    def _rename_os_interface(self, initial_interface_name: str, alias_interface_name: str) -> bool:
        """
        Rename the operating system network interface.

        This method uses the 'ip' command to rename the specified network interface.
        
        Args:
            initial_interface_name (str): The current name of the network interface.
            alias_interface_name (str): The new name to assign to the network interface.

        Returns:
            bool: STATUS_OK if the renaming process is successful, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Error renaming interface: {initial_interface_name} to {alias_interface_name}")
            return STATUS_NOK

        self.log.debug(f"Interface {initial_interface_name} successfully renamed to {alias_interface_name}")
        
        return STATUS_OK

    def get_interface_via_db(self) -> List[str]:
        """
        Get a list of all interface names from DB.

        Returns:
            List[str]: A list containing the names of all interfaces.
        """
        return self.get_db_interface_names()
    
    def flush_interfaces(self, interface_name: str = None) -> bool:
        """
        Flush network interfaces, removing any configurations.

        This method iterates through the list of network interfaces and uses the 'flush_interface' method
        to remove configurations. If a specific interface name is provided, only that interface is flushed.

        Args:
            interface_name (str, optional): The name of the specific network interface to flush.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        if interface_name:
            self.flush_interface(interface_name)
        else:
            for if_name in self.get_interface_via_db():
                self.flush_interface(if_name)

        return STATUS_OK

