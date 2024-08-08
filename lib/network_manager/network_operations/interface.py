import ipaddress
import json
import logging
from typing import List, Optional

from lib.db.interface_db import InterfaceDatabase
from lib.network_manager.common.interface import InterfaceType 
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.network_manager.network_operations.bridge import Bridge
from lib.network_manager.network_operations.arp import Arp, Encapsulate
from lib.network_manager.network_operations.nat import NATDirection, Nat
from lib.network_manager.network_operations.network_mgr import NetworkManager
from lib.network_manager.network_operations.vlan import Vlan

class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class Interface(NetworkManager, InterfaceDatabase):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INTERFACE)
        self.arg = arg

    def clear_interface_arp(self, interface_name: str=None) -> bool:
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
    
    def get_os_network_interfaces(self, interface_type: Optional[InterfaceType] = None) -> List[str]:
        """
        Retrieve network interface names based on their type. If no type is specified, retrieves all interfaces.

        Args:
            interface_type (Optional[InterfaceType]): The type of network interface to retrieve.
                - InterfaceType.LOOPBACK: Retrieve loopback interfaces.
                - InterfaceType.ETHERNET: Retrieve Ethernet interfaces.
                - InterfaceType.WIRELESS: Retrieve wireless interfaces.

        Returns:
            List[str]: A list of network interface names of the specified type, or all if no type is specified.
        """
        command = ['lshw', '-class', 'network', '-short']
        output = self.run(command, suppress_error=True)
        
        if not output.stdout:
            return []

        interfaces = []
        for line in output.stdout.split('\n')[2:]:
            if not line.strip():
                continue
            
            parts = line.split()
            description = ' '.join(parts[1:-1])
            iface_name = parts[1] if len(parts) > 1 else ""

            if interface_type is None:
                interfaces.append(iface_name)
            elif interface_type == InterfaceType.LOOPBACK:
                if 'loopback' in iface_name.lower():
                    interfaces.append(iface_name)
            elif interface_type == InterfaceType.ETHERNET:
                if 'Ethernet' in description:
                    interfaces.append(iface_name)
            elif interface_type == InterfaceType.WIRELESS_WIFI:
                if 'Wireless' in description:
                    interfaces.append(iface_name)

        return interfaces
    
    def does_os_interface_exist(self, interface_name: str, include_loopbacks: bool=True) -> bool:
        """
        Determine if a network interface with the specified name exists on the current system.

        This method utilizes the 'ip -json address show' command to retrieve a list of all network interfaces
        present on the system and subsequently verifies if the provided interface name is included in the
        command's output. It also checks for labeled sub-interfaces of loopback.

        Args:
            interface_name (str): The name of the network interface to be checked.
            include_loopbacks (bool): Whether to include loopback interfaces in the check.

        Returns:
            bool: A boolean value indicating the existence of the specified interface.
            - True: The interface exists.
            - False: otherwise
        """
        try:
            result = self.run(['ip', '-json', 'address', 'show'], suppress_error=True)
            
            if result.exit_code:
                self.log.debug(f"does_os_interface_exist() returned a non-zero exit code: {result.exit_code}")
                return False
            
            interfaces = json.loads(result.stdout)
            
            for interface in interfaces:
                ifname = interface.get("ifname", "")
                
                # Check for the main interface
                if ifname == interface_name:
                    if "loopback" in interface.get("link_type", "") and not include_loopbacks:
                        continue
                    return True
                
                # Check for labeled sub-interfaces under loopback (lo)
                if ifname == "lo" and include_loopbacks:
                    for addr_info in interface.get("addr_info", []):
                        label = addr_info.get("label", "")
                        if label == interface_name:
                            return True

            self.log.debug(f"does_os_interface_exist() '{interface_name}' does not exist")
            return False
                
        except Exception as e:
            self.log.error(f"Exception in does_os_interface_exist: {e}")
            return False

    def get_os_interface_type(self, interface_name: str, include_loopback_labels: bool=True) -> InterfaceType:
        """
        Get the type of a network interface (physical, virtual, or VLAN) based on its name.

        Args:
            interface_name (str): The name of the network interface to query.

        Returns:
            InterfaceType: The type of the interface, which can be 'ETHERNET', 'VIRTUAL', 'VLAN', 'BRIDGE', 'LOOPBACK', or 'UNKNOWN'.
        """
        
        if include_loopback_labels:
            if interface_name in Interface().get_os_lo_labels():
                self.log.debug(f'interface" {interface_name} is a type {InterfaceType.LOOPBACK.value}')
                return InterfaceType.LOOPBACK
        
        result = self.run(['ip', '-json', 'link', 'show', interface_name], suppress_error=True)
        self.log.debug(f"get_os_interface_type() -> stdout: {result.stdout}")

        if result.exit_code:
            self.log.debug(f"get_os_interface_type() -> Interface Not Found: {interface_name}")
            return InterfaceType.UNKNOWN

        try:
            interfaces = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to decode JSON: {e}")
            return InterfaceType.UNKNOWN

        if not interfaces:
            self.log.debug(f"get_os_interface_type() -> No interfaces found for: {interface_name}")
            return InterfaceType.UNKNOWN

        interface = interfaces[0]
        self.log.debug(f"Parsed interface JSON: {interface}")

        link_type = interface.get('link_type', '')
        self.log.debug(f"Detected link type: {link_type}")

        if link_type == 'ether':
            return InterfaceType.ETHERNET
        elif link_type in ['tun', 'tap']:
            return InterfaceType.VIRTUAL
        elif link_type == 'vlan':
            return InterfaceType.VLAN
        elif link_type == 'bridge':
            return InterfaceType.BRIDGE
        elif link_type == 'loopback':
            return InterfaceType.LOOPBACK

        return InterfaceType.UNKNOWN

    def get_os_interface_type_extened(self, interface_name: str) -> InterfaceType:
        """
        Get the type of a network interface using lshw.

        This method retrieves information about the network interface using lshw and determines its type based on the
        capabilities and configuration.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            InterfaceType: An enumeration representing the type of the network interface.
        """
        interface_info = self.get_os_interface_hardware_info(interface_name)
        
        if not interface_info:
            if_type =  self.get_os_interface_type(interface_name)
            return if_type
        
        elif interface_info.get('capabilities', {}).get('wireless'):
            return InterfaceType.WIRELESS_WIFI
        
        elif interface_info.get('capabilities', {}).get('tp'):
            return InterfaceType.ETHERNET
        
        elif interface_info.get('configuration', {}).get('duplex'):
            return InterfaceType.ETHERNET
        
        return self.get_os_interface_type(interface_name)

    def get_db_interface_type(self, interface_name) -> InterfaceType:
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

    def does_db_interface_exist(self, interface_name: str) -> bool:
        """
        Determine if a network interface with the specified name exists on the DB.
        Args:
            interface_name (str): The name of the network interface to be checked.

        Returns:
            bool: A boolean value indicating the existence of the specified interface in the DB.
            - True: The interface exists.
            - False: otherwise
        """        
        return self.db_lookup_interface_exists(interface_name).status

    def add_db_interface_entry(self, interface_name: str, ifType: InterfaceType) -> bool:
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
                self.log.error(f'Unable to update database speed: {speed.value} on interface: {interface_name}')
                return STATUS_NOK
            return STATUS_OK
        
        if speed == Speed.AUTO_NEGOTIATE:
            self.set_speed(interface_name, Speed.AUTO_NEGOTIATE, Speed.AUTO_NEGOTIATE)
            self.update_db_ifSpeed(interface_name, Speed.AUTO_NEGOTIATE.value)
            
        elif speed in {Speed.MBPS_10, Speed.MBPS_100, Speed.MBPS_1000, Speed.MBPS_10000}:
            self.set_speed(interface_name, speed)
            self.update_db_ifSpeed(interface_name, str(speed.value))
        
        else:
            print(f"Invalid speed value: {speed.value}")
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
     
    def create_os_dummy_interface(self, interface_name:str) -> bool:
        """
        Create a dummy interface with the specified name to OS.

        Args:
            interface_name (str): The name for the dummy interface.

        Returns:
            bool: STATUS_OK if the dummy interface was created successfully, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'add', 'name', interface_name , 'type', 'dummy'], suppress_error=True)
        
        if result.exit_code:
            self.log.error(f'Error creating dummy -> {interface_name}, Reason: {result.stderr}')
            return STATUS_NOK
        
        self.log.debug(f'Created {interface_name} Dummy')
        
        return STATUS_OK

    def destroy_os_dummy_interface(self, interface_name: str) -> bool:
        """
        Destroy a dummy interface with the specified name on the OS.

        Args:
            interface_name (str): The name of the dummy interface to destroy.

        Returns:
            bool: STATUS_OK if the dummy interface was destroyed successfully, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'delete', interface_name, 'type', 'dummy'], suppress_error=True)

        if result.exit_code:
            self.log.error(f'Error destroying dummy -> {interface_name}, Reason: {result.stderr}')
            return STATUS_NOK

        self.log.debug(f'Destroyed {interface_name} dummy')
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
            return Vlan().add_interface_by_vlan_id(brName, vlan_id)
        
        else:
            self.log.debug(f"Assigned VLAN: {vlan_id} to interface: {interface_name}")
            return Vlan().add_interface_by_vlan_id(interface_name, vlan_id)
    
    def del_interface_vlan(self, vlan_id:int) -> bool:
        """
        Delete a VLAN to a network interface or bridge.

        Args:
            vlan_id (int): The VLAN ID to assign.

        Returns:
            STATUS_OK if the VLAN assignment was successful, STATUS_NOK is failed
        """
        self.log.debug(f"del_vlan() -> vlan_id: {vlan_id}")

        return Vlan().delete_interface_from_vlan(vlan_id)

    def rename_interface(self, initial_interface_name: str, 
                        alias_interface_name: str, 
                        suppress_error: bool=True) -> bool:
        """
        Rename a network interface to a specified alias name.
        
        This method renames a network interface from `initial_interface_name` to `alias_interface_name`. If the initial 
        interface does not exist, or if the renaming process fails, it logs an error unless `suppress_error` is set to `True`.
        
        Args:
            initial_interface_name (str): The current name of the network interface to be renamed.
            alias_interface_name (str): The new alias name for the network interface.
            suppress_error (bool, optional): If True, suppresses error logging when renaming fails. Defaults to True.
        
        Returns:
            bool: STATUS_OK if the interface was renamed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"rename_interface() -> if: {initial_interface_name} -> alias-if: {alias_interface_name}")
        
        # Check if the initial interface exists
        if not self.does_os_interface_exist(initial_interface_name):
            if not suppress_error:
                self.log.error(f"Interface: {initial_interface_name} does not exist")
            return STATUS_NOK        

        # Get the hardware bus info for the initial interface
        bus_info = self.get_os_interface_hardware_info(initial_interface_name)['businfo']
        
        # Attempt to rename the interface using the `ip` command
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)
        
        # Check if the alias interface already exists in the database
        if self.db_lookup_interface_alias_exist(initial_interface_name, alias_interface_name):
            self.log.debug(f"Alias-Interface already exists: {alias_interface_name} assigned to initial-interface: {initial_interface_name}")
            return STATUS_OK
        
        # If the `ip` command failed, handle the error
        if result.exit_code:
            if not suppress_error:
                self.log.error(f"Unable to rename interface {initial_interface_name} to {alias_interface_name} in the OS")
            return STATUS_NOK
        
        # Update the database with the new alias name
        if self.update_db_rename_alias(bus_info, initial_interface_name, alias_interface_name):
            if not suppress_error:
                self.log.error(f"Unable to add initial-interface: {initial_interface_name} to alias-interface: {alias_interface_name} in the DB")
            return STATUS_NOK
        
        return STATUS_OK
       
    def set_os_rename_interface(self, reverse=False, suppress_error: bool=True) -> bool:
        """
        Rename network interfaces based on database aliases.
        
        This method renames network interfaces as specified in the database. It can also reverse the renaming process
        if the `reverse` parameter is set to `True`. If an error occurs during the renaming process, it logs an error 
        message unless `suppress_error` is set to `True`.
        
        Args:
            reverse (bool, optional): If True, reverses the renaming process by swapping original and alias names. 
                                    Defaults to False.
            suppress_error (bool, optional): If True, suppresses error logging when renaming fails. Defaults to True.
        
        Returns:
            bool: STATUS_OK if all interfaces were renamed successfully, STATUS_NOK otherwise.
        """
        for alias in self.get_db_interface_aliases():
            original_name = alias['InterfaceName']
            alias_name = alias['AliasInterface']

            self.log.debug(f'orig-interface: {original_name} -> new-interface: {alias_name}')

            if reverse:
                original_name, alias_name = alias_name, original_name

            if self._rename_os_interface(original_name, alias_name):
                if not suppress_error:
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

    def get_os_interface_hardware_info(self, interface_name: str) -> dict:
        """
        Retrieve information about hardware network interfaces.

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
        for if_name in self.get_os_network_interfaces():
            
            if interface_name is not None and if_name != interface_name or not self.db_lookup_interface_exists(if_name):
                self.log.debug(f"Unknown interface: {if_name}")
                continue
            
            if_type = self.get_os_interface_type_extened(if_name)
                       
            if if_type != InterfaceType.UNKNOWN:
                self.log.debug(f"Adding Interface: {if_name} -> if-type: {if_type.name} to DB")
                self.add_db_interface_entry(if_name, if_type)
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

    def fetch_db_interface_names(self) -> List[str]:
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
            for if_name in self.get_db_interface_names():
                self.flush_interface(if_name)

        return STATUS_OK

    # LoopBack Operations

    def get_os_lo_labels(self) -> List[str]:
        """
        Extract labels from the loopback interface labels

        Args:
            ip_lo_json (dict): The JSON data structure for the loopback interface.

        Returns:
            List[str]: A list of labels found in the loopback interface's address information.
        """
        labels = []
        
        try:
            result = self.run(['ip', '-json', 'address', 'show', 'dev', 'lo'], suppress_error=True)
            
            if result.exit_code:
                self.log.debug(f"does_os_interface_exist() returned a non-zero exit code: {result.exit_code}")
                return []
                            
        except Exception as e:
            self.log.error(f"Exception in does_os_interface_exist: {e}")
            return []

        interfaces = json.loads(result.stdout)
        
        for interface in interfaces:
            ifname = interface.get("ifname", "")
                            
            if ifname == "lo":
                for addr_info in interface.get("addr_info", []):
                    label = addr_info.get("label", "lo")
                    labels.append(label.split(":")[-1])

        return labels

    def create_os_loopback(self, loopback_name: str, inet_address: str) -> bool:
        """
        Creates a loopback interface with the specified name (label) and IP address on the 'lo' device.

        Args:
            loopback_name (str): The name (label) for the new loopback interface.
            inet_address (str): The IP address to assign to the loopback interface.

        Returns:
            bool: STATUS_OK if the loopback interface was created successfully, otherwise STATUS_NOK.
        """
        
        if loopback_name in self.get_os_lo_labels():
            self.log.debug(f"Loopback interface {loopback_name} already exists.")
            return STATUS_NOK
        
        try:
            ip = ipaddress.ip_address(inet_address)
            if ip.version == 4:
                ip_ver_opt = 'addr'
                cidr = '/32'
            elif ip.version == 6:
                ip_ver_opt = '-6 addr'
                cidr = '/128'
            else:
                self.log.error(f'inet address is invalid: {inet_address}')
                return STATUS_NOK
            
        except ValueError:
            self.log.error(f'inet address is invalid: {inet_address}')
            return STATUS_NOK

        inet_address += cidr

        command = ['ip', ip_ver_opt, 'add', inet_address, 'label', f'lo:{loopback_name}', 'dev', 'lo']
        
        rtn = self.run(command, suppress_error=True)
        
        if rtn.exit_code != 0:
            self.log.error(f"Failed to create loopback interface {loopback_name} with address {inet_address}: {rtn.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def set_db_loopback(self, loopback_name: str, inet_address_cidr: str) -> bool:
        """
        Sets a loopback interface in the database with the specified name and IP address in CIDR notation.

        Args:
            loopback_name (str): The name (label) for the loopback interface.
            inet_address_cidr (str): The IP address with CIDR notation to assign to the loopback interface.

        Returns:
            bool: STATUS_OK if the loopback interface was set successfully, otherwise STATUS_NOK.
        """
        
        # Attempt to add the loopback interface entry to the database
        if not self.add_db_interface_entry(interface_name=loopback_name, ifType=InterfaceType.LOOPBACK):
            self.log.error(f'Unable to add Loopback interface: {loopback_name}')
            return STATUS_NOK
        
        # Attempt to update the IP address for the loopback interface in the database
        if not self.update_db_inet_address(interface_name=loopback_name, inet_address_cidr=inet_address_cidr):
            self.log.error(f'Unable to update inet address for Loopback interface: {loopback_name} with address: {inet_address_cidr}')
            # Remove the interface entry since the IP address update failed
            self.del_db_loopback(loopback_name)
            return STATUS_NOK
        
        return STATUS_OK
    
    def destroy_os_loopback(self, loopback_name: str, inet_address: str) -> bool:
        """
        Destroys a loopback interface with the specified name (label) and IP address from the 'lo' device.

        Args:
            loopback_name (str): The name (label) for the loopback interface to be removed.
            inet_address (str): The IP address assigned to the loopback interface.

        Returns:
            bool: STATUS_OK if the loopback interface was removed successfully, otherwise STATUS_NOK.
        """
        
        if loopback_name not in self.get_os_lo_labels():
            self.log.debug(f"Loopback interface {loopback_name} does not exist.")
            return STATUS_NOK
        
        try:
            ip = ipaddress.ip_address(inet_address)
            if ip.version == 4:
                ip_ver_opt = 'addr'
                cidr = '/32'
            elif ip.version == 6:
                ip_ver_opt = '-6 addr'
                cidr = '/128'
            else:
                self.log.error(f'inet address is invalid: {inet_address}')
                return STATUS_NOK
            
        except ValueError:
            self.log.error(f'inet address is invalid: {inet_address}')
            return STATUS_NOK

        inet_address += cidr

        command = ['ip', ip_ver_opt, 'del', inet_address, 'label', f'lo:{loopback_name}', 'dev', 'lo']
        
        rtn = self.run(command, suppress_error=True)
        
        if rtn.exit_code != 0:
            self.log.error(f"Failed to destroy loopback interface {loopback_name} with address {inet_address}: {rtn.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def del_db_loopback(self, loopback_name: str) -> bool:
        """
        Deletes a loopback interface from the database with the specified name.

        Args:
            loopback_name (str): The name (label) of the loopback interface to be deleted.

        Returns:
            bool: STATUS_OK if the loopback interface was deleted successfully, otherwise STATUS_NOK.
        """
        
        if not self.del_db_interface(loopback_name):
            self.log.error(f'Unable to delete Loopback interface: {loopback_name}')
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_next_loopback_address(self) -> str:
        """
        Search the lo interface, retrieve a list of IPv4 addresses in the 127.x.x.x range,
        and find the next available address in that range.

        Returns:
            str: The next available 127.x.x.x address in CIDR notation.
        """
        try:
            # Get the list of addresses on the loopback interface in JSON format
            result = self.run(['ip', '-j', 'addr', 'show', 'dev', 'lo'], suppress_error=True)

            if result.exit_code != 0:
                self.log.error(f"Error retrieving IP addresses: {result.stderr}")
                return None

            data = json.loads(result.stdout)

            # Collect all 127.x.x.x addresses
            addresses = [
                ipaddress.ip_interface(f"{addr_info['local']}/{addr_info['prefixlen']}").ip
                for iface in data if iface['ifname'] == 'lo'
                for addr_info in iface.get('addr_info', [])
                if addr_info['family'] == 'inet' and ipaddress.ip_interface(f"{addr_info['local']}/{addr_info['prefixlen']}").ip.is_loopback
            ]

            # Sort addresses and find the highest one
            addresses.sort()
            last_address = addresses[-1] if addresses else ipaddress.IPv4Address('127.0.0.0')

            # Calculate the next available address
            next_address = last_address + 1
            if next_address.is_loopback:
                next_address_cidr = f"{next_address}/8"
                return next_address_cidr
            else:
                self.log.error("No more available 127.x.x.x addresses")
                return None

        except Exception as e:
            self.log.error(f"An error occurred: {e}")
            return None

    def update_interface_loopback_inet(self, loopback_name: str, inet_address_cidr: str = None, negate: bool = False) -> bool:
        """
        Update or delete the inet address of a loopback interface.

        This function updates the inet address of a specified loopback interface. If the negate parameter is set to True,
        it attempts to delete the specified inet address from the loopback interface. Otherwise, it sets the specified
        inet address. If no address is provided, it attempts to auto-assign the next available inet address.

        Parameters:
        loopback_name (str): The name of the loopback interface to update.
        inet_address_cidr (str, optional): The inet address in CIDR notation to set or delete. If None, the next available
                                        address is auto-assigned. Defaults to None.
        negate (bool): If True, the inet address is deleted from the loopback interface. If False, the address is set.
                    Defaults to False.

        Returns:
        bool: STATUS_OK if the operation was successful, otherwise STATUS_NOK.
        """
        self.log.debug(f"update_interface_loopback_inet() - Loopback: {loopback_name}, "
                    f"Inet: {inet_address_cidr}, Negate: {negate}")

        if negate:
            if not self.del_inet_address_loopback(loopback_name, inet_address_cidr):
                self.log.error(f"Unable to delete loopback: {loopback_name} address: {inet_address_cidr} from OS")
                return STATUS_NOK

            if not self.del_db_interface(loopback_name):
                self.log.error(f"Unable to delete loopback: {loopback_name} address: {inet_address_cidr} from DB")
                return STATUS_NOK

        else:
            if not inet_address_cidr:
                inet_address_cidr = self.get_next_loopback_address()
                if not inet_address_cidr:
                    self.log.error("Unable to get next available loopback address")
                    return STATUS_NOK

                self.log.debug(f'Auto-Assign Loopback: {loopback_name} - inet: {inet_address_cidr}')

            if self.set_inet_address_loopback(loopback_name, inet_address_cidr):
                self.log.error(f"Unable to update loopback: {loopback_name} address: {inet_address_cidr} to OS")
                return STATUS_NOK

            if self.add_db_interface(loopback_name, InterfaceType.LOOPBACK):
                self.log.error(f"Unable to update loopback: {loopback_name} to DB")
                return STATUS_NOK

        return STATUS_OK
