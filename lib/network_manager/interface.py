import argparse
from enum import Enum, auto
import json
import logging
import re
from typing import Optional

from tabulate import tabulate
from lib.network_manager.bridge import Bridge, BridgeProtocol as BrProc
from lib.network_manager.vlan import Vlan
from lib.network_manager.network_manager import NetworkManager
from lib.network_manager.nat import Nat, NATDirection
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.network_manager.phy import Duplex, Speed, State

class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class InterfaceType(Enum):
    PHYSICAL = 'phy'
    ETHERNET = 'if'
    VLAN = 'vlan'
    LOOPBACK = 'loopback'
    VIRTUAL = 'vir'
    BRIDGE = 'br'
    UNKNOWN = auto()
        
class Interface(NetworkManager):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg

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


    def get_interface_type(self, interface_name:str) -> InterfaceType:
        """
            Get the type of a network interface (physical, virtual, or VLAN) based on its name.

            Args:
                interface_name (str): The name of the network interface to query.

            Returns:
                str: The type of the interface, which can be 'Physical', 'Virtual', 'VLAN', or 'Unknown'.
                    Returns 'None' if the interface is not found.
        """

        result = self.run(['ip', 'link', 'show' , interface_name])
        self.log.debug(f"get_interface_type() -> sdtout: {result.stdout}")
        
        if result.exit_code:
            self.log.debug(f"get_interface_type() -> Interface Not Found: {interface_name}")
            return InterfaceType.UNKNOWN
        
        # Split the output into lines
        lines = result.stdout.split('\n')
        
        for line in lines:
            self.log.debug(f"Line {line}")
            # Check if it's a physical interface
            if 'link/ether' in line:
                return InterfaceType.ETHERNET
            # Check if it's a virtual interface
            elif 'link/tun' in line or 'link/tap' in line:
                return InterfaceType.VIRTUAL
            # Check if it's a VLAN interface
            elif 'vlan' in line:
                return InterfaceType.VLAN
            elif 'bridge' in line:
                return InterfaceType.BRIDGE
            
        return InterfaceType.UNKNOWN

    def does_interface_exist(self, ifName:str) -> bool:
        """
        Check if a network interface with the given name exists on the system.

        This method uses the 'ip link' command to list all network interfaces on
        the system and checks if the specified interface name exists in the output.

        Args:
            ifName (str): The name of the network interface to check.

        Returns:
            bool: A status indicating whether the interface is valid or not.
                - STATUS_OK: If the interface exists.
                - STATUS_NOK: If the interface does not exist or an error occurred.
        """
        command = ['ip', 'link', 'show', ifName]

        try:
            result = self.run(command, suppress_error=True)

            if result.exit_code == 0:
                return STATUS_OK
            else:
                self.log.debug(f"does_interface_exist return a non-zero: {result.exit_code}")
                return STATUS_NOK
        except Exception as e:
            print(f"Error: {e}")
            return STATUS_NOK
        
    def set_if_mac(self, ifName: str, mac: Optional[str] = None) -> bool:
        """
        Add a MAC address to a network interface.

        This method either generates a random MAC address or uses the provided MAC address
        (if valid) and assigns it to the specified network interface.

        Args:
            ifName (str): The name of the network interface to which the MAC address will be assigned.
            mac (str, optional): The MAC address to assign. If not provided or invalid, a random MAC address
                will be generated.

        Returns:
            bool: True if the MAC address was successfully added, False otherwise.

        Raises:
            None

        Example:
            To add a MAC address to 'eth0':
            >>> add_mac('eth0', '00:11:22:33:44:55')
        """
        self.log.debug(f"add_mac() -> ifName: {ifName} -> mac: {mac}")

        if not mac:
            # Generate a random MAC address
            new_mac = self.generate_random_mac()
            self.update_if_mac_address(ifName, new_mac)
        elif self.is_valid_mac_address(mac) == STATUS_OK:
            # Format and assign the provided MAC address
            stat, format_mac = self.format_mac_address(mac)
            self.log.debug(f"add_mac() -> mac: {mac} -> format_mac: {format_mac}")
            self.update_if_mac_address(ifName, format_mac)
        else:
            print(f"Invalid MAC address: {mac}")
            return STATUS_NOK

        return STATUS_OK

    def set_if_ipv6(self, ifName: str, ipv6_address_mask: str):
        """
        Add an IPv6 address to a network interface.

        This method validates the IPv6 address and adds it to the specified network interface.

        Args:
            ifName (str): The name of the network interface to which the IPv6 address will be added.
            ipv6_address_mask (str): The IPv6 address with prefix length (e.g., '2001:db8::1/64').

        Returns:
            None

        Raises:
            InvalidInterface: If the provided IPv6 address is invalid or if adding the address fails.

        Example:
            To add an IPv6 address to 'eth0':
            >>> add_ipv6('eth0', '2001:db8::1/64')
        """
        if not self.is_valid_ipv6(ipv6_address_mask):
            raise InvalidInterface(f"Invalid IPv6 Address: {ipv6_address_mask}")

        if self.set_inet6_address(ifName, ipv6_address_mask):
            raise InvalidInterface(f"Unable to add IPv6 Address: {ipv6_address_mask}")

    def set_if_ip(self, ipv4_address: str, subnet_mask: str):
        """
        Add an IPv4 address to a network interface.

        This method validates the IPv4 address and subnet mask and adds them to the specified network interface.

        Args:
            ipv4_address (str): The IPv4 address (e.g., '192.168.1.1').
            subnet_mask (str): The IPv4 subnet mask (e.g., '255.255.255.0').

        Returns:
            None

        Raises:
            InvalidInterface: If the provided IPv4 address or subnet mask is invalid
                or if adding the address fails.

        Example:
            To add an IPv4 address to 'eth0':
            >>> add_ip('192.168.1.1', '255.255.255.0')
        """
        if not self.is_valid_ipv4(ipv4_address):
            raise InvalidInterface(f"Invalid IPv4 Address: {ipv4_address}")

        if not self.is_valid_ipv4(subnet_mask):
            raise InvalidInterface(f"Invalid IPv4 Subnet: {subnet_mask}")

        if self.set_inet_address(self.ifName, ipv4_address, subnet_mask):
            raise InvalidInterface(f"Unable to add IPv4 Address: {ipv4_address}")

    def set_if_duplex(self, ifName: str, duplex: Duplex) -> bool:
        """
        Add or set the duplex mode for a network interface.

        This method allows adding or setting the duplex mode to 'auto', 'half', or 'full' for the specified interface.

        Args:
            ifName (str): The name of the network interface to configure.
            duplex (Duplex): The duplex mode to set. Valid values are Duplex.AUTO, Duplex.HALF, or Duplex.FULL.

        Returns:
            bool: A status string indicating the result of the operation. 'STATUS_OK' if successful,
                 'STATUS_NOK' if an invalid duplex mode is provided.
                 
        """
        if self.set_duplex(ifName, duplex):
            print("Invalid duplex mode. Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
        
        return STATUS_OK
    
    def set_if_speed(self, args):
        '''
        Set the speed of a network interface.
        Usage: speed <10 | 100 | 1000 | 10000 | auto>
        '''
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 10000 | auto>")
            return

        self.log.debug(f"do_speed() -> ARGS: {args}")
        
        speed_values = {str(s.value): s for s in Speed}
        args = args.lower()

        if args == "auto":
            self.set_ifSpeed(self.ifName, Speed.MBPS_10, Speed.AUTO_NEGOTIATE)

        elif args in speed_values:
            speed = speed_values[args]
            self.set_ifSpeed(self.ifName, speed)
        else:
            print("Invalid speed value. Use '10', '100', '1000', '10000', or 'auto'.")
            
    def set_shutdown(self, ifName: str, state: State) -> bool:
        """
        Set the shutdown status of a network interface.

        This method allows setting the shutdown status of the specified network interface to 'up' or 'down'.

        Args:
            ifName (str): The name of the network interface to configure.
            status (State): The status to set. Valid values are State.UP (to bring the interface up)
                           or State.DOWN (to shut the interface down).

        Returns:
            bool: True if the operation was successful, False otherwise.

        """
        self.log.debug(f"set_shutdown() -> ifName: {ifName} -> State: {state}")
        return self.set_interface_state(ifName, state)
    
    def set_bridge_group(self, ifName:str, br_id:str, stp_protocol:BrProc=BrProc.IEEE_802_1D) -> bool:
        """
        Set the bridge group and Spanning Tree Protocol (STP) configuration for a network interface.

        This method allows configuring a network interface to be a part of a specific bridge group with optional STP protocol selection.

        Args:
            ifName (str): The name of the network interface to configure.
            br_id (str): The identifier of the bridge group to join.
            stp_protocol (BrProc): The STP protocol to use for the bridge group (default is IEEE 802.1D).

        Returns:
            bool: A status string indicating the result of the operation. 'STATUS_OK' if successful,
                 'STATUS_NOK' if the specified bridge group does not exist.

        """
        if Bridge().add_interface_cmd(ifName, br_id, stp_protocol) == STATUS_NOK:
            print(f"bridge-group {br_id} does not exists")
            return STATUS_NOK
        return STATUS_OK
    
    def create_loopback(self, ifName:str) -> bool:
        """
        Create a loopback interface with the specified name.

        Args:
            ifName (str): The name for the loopback interface.

        Returns:
            bool: True if the loopback interface was created successfully, False otherwise.
        """
        result = self.run(['ip', 'link', 'add', 'name', ifName , 'type', 'dummy'])
        if result.exit_code:
            self.log.error("Error creating loopback -> {ifName}")
            return STATUS_NOK
        
        self.log.debug(f"Created {ifName} Loopback")
        return STATUS_OK
    
    def set_vlan(self, ifName:str, vlan_id:int=1000):
        """
        Assign a VLAN to a network interface or bridge.

        Args:
            ifName (str): The name of the network interface.
            vlan_id (int, optional): The VLAN ID to assign. Defaults to 1000.

        Returns:
            STATUS_OK if the VLAN assignment was successful, STATUS_NOK is failed
        """
        self.log.debug(f"set_vlan() -> ifName: {ifName} vlan_id: {vlan_id}")

        # Check to see if the interface is part of a bridge to assign the VLAN to the bridge
        brName = Bridge().get_assigned_bridge_from_interface(ifName)

        if brName:
            self.log.debug(f"Assigned VLAN: {vlan_id} to Bridge: {brName}")
            return Vlan().add_interface_to_vlan(brName, vlan_id)
        else:
            self.log.debug(f"Assigned VLAN: {vlan_id} to interface: {ifName}")
            return Vlan().add_interface_to_vlan(ifName, vlan_id)
    
    def del_vlan(self, vlan_id:int) -> bool:
        """
        Delete a VLAN to a network interface or bridge.

        Args:
            vlan_id (int): The VLAN ID to assign.

        Returns:
            STATUS_OK if the VLAN assignment was successful, STATUS_NOK is failed
        """
        self.log.debug(f"del_vlan() -> vlan_id: {vlan_id}")

        return Vlan().del_interface_to_vlan(vlan_id)

    def rename_interface(self, current_ifName:str, new_ifName:str) -> bool:
        """
        Rename a network interface

        Args:
            current_ifName (str): The current name of the network interface.
            new_ifName (str): The new name to assign to the network interface.

        Returns:
            bool: STATUS_OK if the interface was successfully renamed, STATUS_NOK otherwise.
        """
                
        self.log.debug(f"rename_interface() -> Curr-if: {current_ifName} -> new-if: {new_ifName}")
        
        '''sudo ip link set <current_ifName> name <new_ifName>'''
        result = self.run(['ip', 'link', 'set', current_ifName, 'name', new_ifName])
        
        if result.exit_code:
            self.log.error(f"Unable to rename interface {current_ifName} to {new_ifName}")
            return STATUS_NOK
        
        return STATUS_OK        

    def set_nat_domain_status(self, ifName:str, nat_in_out:NATDirection, negate=False):
        
        if nat_in_out is NATDirection.INSIDE:
            if Nat().create_inside_nat(ifName):
                self.log.error(f"Unable to add INSIDE NAT to interface: {ifName}")
                return STATUS_NOK
        else:
            if Nat().create_outside_nat(ifName):
                self.log.error(f"Unable to add INSIDE NAT to interface: {ifName}")
                return STATUS_NOK
            
        return STATUS_OK        
