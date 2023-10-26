import ipaddress
import json
import logging
import re
from typing import Optional

from lib.db.interface_db import InterfaceDatabase

from lib.network_manager.bridge import Bridge, BridgeProtocol as BrProc
from lib.network_manager.vlan import Vlan
from lib.network_manager.network_manager import InterfaceType, NetworkManager
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
                - False: The interface is not found or an error has occurred.
        """

        command = ['ip', 'link', 'show', interface_name]

        try:
            result = self.run(command, suppress_error=True)

            if result.exit_code == 0:
                return True
            else:
                self.log.debug(f"does_interface_exist return a non-zero: {result.exit_code}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        
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

        if self.update_mac_address_db(interface_name, new_mac if not mac else format_mac):
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
                self.log.debug(f"Unable to remove inet Address: {inet_address} from interface: {interface_name} via OS")
                return STATUS_NOK
            
        else:
            if self.set_inet_address(interface_name, inet_address, secondary):
                self.log.debug(f"Unable to add inet Address: {inet_address} to interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_inet_address_db(interface_name, inet_address, secondary, negate):
            self.log.debug(f"Unable to add inet Address: {inet_address} to interface: {interface_name} via DB")
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
        if self.set_duplex(interface_name, duplex):
            print(f"Invalid duplex mode ({duplex.value}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
        
        if self.update_duplex_status_db(interface_name, duplex.value):
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

        if speed == Speed.AUTO_NEGOTIATE:
            self.set_speed(interface_name, Speed.AUTO_NEGOTIATE, Speed.AUTO_NEGOTIATE)
            self.update_ifSpeed_db(interface_name, Speed.AUTO_NEGOTIATE.value)
            0
        elif speed in {Speed.MBPS_10, Speed.MBPS_100, Speed.MBPS_1000, Speed.MBPS_10000}:
            self.set_speed(interface_name, speed)
            self.update_ifSpeed_db(interface_name, speed.value)
        
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
        
        # Determine the value of 'shutdown' based on 'state'
        shutdown = state == State.UP
        
        if self.update_shutdown_status(interface_name, shutdown):
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
        result = self.run(['ip', 'link', 'add', 'name', interface_name , 'type', 'dummy'])
        if result.exit_code:
            self.log.error("Error creating loopback -> {interface_name}")
            return STATUS_NOK
        
        self.log.debug(f"Created {interface_name} Loopback")
        return STATUS_OK
    
    def update_interface_vlan(self, interface_name:str, vlan_id:int=1000):
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

        # Check to see if the interface is part of a bridge to assign the VLAN to the bridge
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

    def rename_interface(self, current_interface_name:str, new_interface_name:str) -> bool:
        """
        Rename a network interface

        Args:
            current_interface_name (str): The current name of the network interface.
            new_interface_name (str): The new name to assign to the network interface.

        Returns:
            bool: STATUS_OK if the interface was successfully renamed, STATUS_NOK otherwise.
        """
                
        self.log.debug(f"rename_interface() -> Curr-if: {current_interface_name} -> new-if: {new_interface_name}")
        
        '''sudo ip link set <current_interface_name> name <new_interface_name>'''
        result = self.run(['ip', 'link', 'set', current_interface_name, 'name', new_interface_name])
        
        if result.exit_code:
            self.log.error(f"Unable to rename interface {current_interface_name} to {new_interface_name}")
            return STATUS_NOK
        
        return STATUS_OK        

    def set_nat_domain_status(self, interface_name:str, nat_in_out:NATDirection, negate=False):
        
        if nat_in_out is NATDirection.INSIDE:
            if Nat().create_inside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
        else:
            if Nat().create_outside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
            
        return STATUS_OK        
