import logging
import re
from typing import List
from lib.network_manager.dhcp_client import DHCPVersion

from lib.network_manager.nat import Nat, NATDirection
from lib.db.sqlite_db.router_shell_db import Result, RouterShellDB as RSDB
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType

class InterfaceDatabase:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().INTERFACE_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()  
            
    def db_lookup_interface_exists(cls, interface_name: str) -> Result:
        """
        Check if an interface with the given name exists in the database.

        Args:
            interface_name (str): The name of the interface to check.

        Returns:
            Result: A Result object with the status and row ID of the existing interface.

        Example:
            You can use this method to determine whether a specific interface exists in the database.
            For instance, you might check if 'GigabitEthernet0/1' exists.

        Note:
            - The 'Result' object returned indicates the status of the interface existence.
            - 'status' True means the interface exists, and 'status' False means it does not.
        """
        return cls.rsdb.interface_exists(interface_name)

    def add_db_interface(cls, interface_name: str, interface_type: InterfaceType, shutdown_status: bool = True) -> bool:
        """
        Add an interface to the database.

        Args:
            interface_name (str): The name of the interface to add.
            interface_type (str): The type of the interface.
            shutdown_status (bool, optional): True if the interface is shutdown, False otherwise (default is True).

        Returns:
            bool: STATUS_OK if the interface was successfully added, STATUS_NOK if there was an issue.
        """
        cls.log.debug(f"add_interface() -> {interface_name} -> {interface_type} -> {shutdown_status}")
        
        result = cls.rsdb.insert_interface(interface_name, interface_type, shutdown_status)

        if result.status:
            cls.log.debug(f"add_interface() - Unable to add interface to DB -> {result.reason}")
            return STATUS_NOK
        
        return STATUS_OK

    def del_db_interface(cls, interface_name: str) -> bool:
        """
        Delete an interface from the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to delete.

        Returns:
            bool: STATUS_OK if the deletion was successful, STATUS_OK otherwise.
        """
        result = cls.rsdb.delete_interface(interface_name)
        
        return result.status
 
    def update_db_shutdown_status(cls, interface_name: str, shutdown_status: bool) -> bool:
        """
        Update the shutdown status of an interface in the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to update.
            shutdown_status (bool): The new shutdown status.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_shutdown(interface_name, shutdown_status)
        return result.status

    def update_db_duplex(cls, interface_name: str, duplex: str) -> bool:
        """
        Update the duplex status of an interface in the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to update.
            duplex (str): The new duplex status.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.update_interface_duplex(interface_name, duplex).status
    
    def update_db_mac_address(cls, interface_name: str, mac_address: str) -> bool:
        """
        Update the MAC address setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            mac_address (str): MAC address in the format xx:xx:xx:xx:xx:xx.

        Returns:
            bool: STATUS_OK if the MAC address was successfully updated, STATUS_NOK otherwise.
        """

        # Check MAC address format using a regular expression
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')

        if not mac_pattern.match(mac_address):
            cls.log.error(f"Invalid mac address format: {mac_address} -> xx:xx:xx:xx:xx:xx")
            return STATUS_NOK

        result = cls.rsdb.update_interface_mac_address(interface_name, mac_address)
        return result.status

    def update_db_ifSpeed(cls, interface_name: str, speed: str) -> bool:
        """
        Update the speed setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            speed (str): The speed setting (e.g., '10', '100', '1000', '10000', 'auto', None).

        Returns:
            bool: STATUS_OK if the speed was successfully updated, STATUS_NOK otherwise.
        """
        cls.log.debug(f"update_speed() -> Interface: {interface_name} -> Speed: {speed}")
        
        result = cls.rsdb.update_interface_speed(interface_name, speed)
        return result.status

    def update_db_inet_address(cls, interface_name, inet_address_cidr, secondary=False, negate=False) -> bool:
        """
        Update or delete an IP address setting for an interface.

        Args:
            interface_name (str): The name of the interface.
            inet_address_cidr (str): The IP address/mask to update or delete.
            secondary (bool): True if the IP address is secondary, False otherwise.
            negate (bool): True to delete the IP address, False to update.

        Returns:
            bool: bool: STATUS_OK if the speed was successfully updated, STATUS_NOK otherwise.
        """
        if not negate:
            result = cls.rsdb.insert_interface_inet_address(interface_name, inet_address_cidr, secondary)
        else:
            result = cls.rsdb.delete_interface_inet_address(interface_name, inet_address_cidr)

        return result.status
    
    def add_line_to_interface(cls, line: str) -> bool:
        """
        Add a router CLI command to the database to save as a configuration.

        Args:
            line (str): The router CLI command to be added to the database.

        Returns:
            bool: STATUS_OK if the command was successfully added to the database, STATUS_NOK otherwise.

        Example:
            You can use this method to save router CLI commands to the database for configuration management.
            For instance, you might add a line like 'interface GigabitEthernet0/0' to configure an interface.

        Usage:
            if add_line_to_interface('interface GigabitEthernet0/0'):
                print("Command added to the database.")
            else:
                print("Failed to add the command.")

        Note:
            - This method stores router CLI commands for configuration purposes.
            - STATUS_OK indicates a successful addition, while STATUS_NOK indicates a failure.
        """
        return STATUS_OK
    
    def update_db_proxy_arp(cls, interface_name: str, status: bool) -> bool:
        """
        Update the Proxy ARP status for a network interface to DB

        Args:
            interface_name (str): The name of the network interface.
            status (bool): The new Proxy ARP status (True for enabled, False for disabled).

        Returns:
            Result: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        cls.log.debug(f"update_proxy_arp_db() -> Interface: {interface_name} -> status:{status}")
        result = cls.rsdb.update_interface_proxy_arp(interface_name, status)
        return result.status

    def update_db_drop_gratuitous_arp(cls, interface_name: str, status: bool) -> bool:
        """
        Update the Drop Gratuitous ARP status for a network interface.

        Args:
            interface_name (str): The name of the network interface.
            status (bool): The new Drop Gratuitous ARP status (True for enabled, False for disabled).

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_drop_gratuitous_arp(interface_name, status)
        return result.status
    
    def update_db_static_arp(cls, interface_name: str, ip_address: str, mac_address: str, encapsulation: str='arpa', negate=False) -> bool:
        """
        Update a static ARP record in the 'InterfaceStaticArp' table.

        Args:
            ip_address (str): The IP address to update.
            mac_address (str): The new MAC address in the format: xx:xx:xx:xx:xx:xx.
            encapsulation (str): The new encapsulation type, e.g., 'arpa' or 'TBD'.
            negate (bool): True to negate the update (i.e., remove the record), False to perform the update.

        Returns:
            bool: STATUS_OK if the update (or deletion) was successful, STATUS_NOK otherwise.
        """
        
          
        if not negate:
            cls.log.debug(f"update_static_arp(INSERT) Interface: {interface_name} -> Arp: -> inet: {ip_address} mac: {mac_address}")
            result = cls.rsdb.update_interface_static_arp(interface_name, ip_address, mac_address, encapsulation)
        else:
            cls.log.debug(f"update_static_arp(DELETE) Interface: {interface_name} -> Arp: -> inet: {ip_address}")
            result = cls.rsdb.delete_interface_static_arp(interface_name, ip_address)

        return result.status

    def update_db_nat_direction(cls, interface_name: str, nat_pool_name: str, nat_direction: NATDirection, negate: bool = False) -> bool:
        """
        Update a NAT direction configuration for a specified interface and NAT pool.

        Args:
            interface_name (str): The name of the interface for the NAT direction.
            nat_pool_name (str): The name of the NAT pool associated with the direction.
            nat_direction (NATDirection): The NAT direction to update.
            negate (bool): Whether to negate the update (i.e., remove the direction if True) (default: False).

        Returns:
            bool: True if the update was successful, False otherwise.

        This method allows you to update a NAT direction configuration for a specific interface and NAT pool. 
        You can either add or remove a NAT direction, based on the `negate` parameter.

        Args:
            - interface_name (str): The name of the interface for the NAT direction.
            - nat_pool_name (str): The name of the NAT pool associated with the direction.
            - nat_direction (NATDirection): The NAT direction to update.
            - negate (bool): If True, the method will remove the NAT direction. If False, it will add the direction (default: False).

        Returns:
            - bool: STATUS_OK if the update was successful, STATUS_NOK if there was an error during the update.

        """
        try:
            if not cls.rsdb.global_nat_pool_name_exists(nat_pool_name):
                cls.log.debug(f"NAT pool '{nat_pool_name}' not found. Update aborted.")
                return STATUS_NOK

            interface_result = cls.db_lookup_interface_exists(interface_name)
            if not interface_result.status:
                cls.log.debug(f"Interface '{interface_name}' not found. Update aborted.")
                return STATUS_NOK

            if negate:
                cls.log.debug(f"Deleting NAT direction: {nat_direction.value} -> interface '{interface_name}' -> NAT Pool '{nat_pool_name}'")
                result = cls.rsdb.delete_interface_nat_direction(interface_name, nat_pool_name)
                if result.status:
                    cls.log.error(f"Unable to delete NAT direction: {nat_direction.value} -> interface '{interface_name}' -> NAT Pool '{nat_pool_name}' error: {result.reason}")
                    return STATUS_NOK
            else:
                cls.log.debug(f"Inserting NAT direction: {nat_direction.value} -> Interface '{interface_name}' -> NAT Pool '{nat_pool_name}'")
                result = cls.rsdb.insert_interface_nat_direction(interface_name, nat_pool_name, nat_direction.value)
                if result.status:
                    cls.log.error(f"Unable to Insert NAT direction: {nat_direction.value} -> interface '{interface_name}' -> NAT Pool '{nat_pool_name}' error: {result.reason}")
                    return STATUS_NOK
            
            return result.status == STATUS_OK

        except Exception as e:
            error_message = f"Error updating NAT direction: {e}"
            cls.log.error(error_message)
            return STATUS_NOK

    def update_db_bridge_group(cls, interface_name: str, bridge_group: str, negate: bool = False) -> bool:
        """
        Update the bridge group for an interface.

        Args:
            interface_name (str): The name of the interface to update.
            bridge_group (str): The name of the bridge group to assign or remove.
            negate (bool):  If True, remove the interface from the bridge group. 
                            If False, assign the interface to the bridge group.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        if negate:
            result = cls.rsdb.delete_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Removed interface '{interface_name}' from bridge group '{bridge_group}'")
        else:
            result = cls.rsdb.insert_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Assigned interface '{interface_name}' to bridge group '{bridge_group}'")

        return STATUS_OK if result.status == STATUS_OK else STATUS_NOK

    def update_db_vlan_to_interface_type(cls, vlan_id: int, interface_type_name: str, interface_type: InterfaceType, negate: bool = False) -> bool:
        """
        Update the VLAN configuration for a specific interface type.

        Args:
            vlan_id (int): The VLAN ID to configure.
            interface_type_name (str): The name of the interface type (BridgeName or InterfaceName) to update.
            interface_type (InterfaceType): The new interface type (BRIDGE or ETHERNET).
            negate (bool, optional): True to negate the configuration, False otherwise. Defaults to False.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        pass

    def update_db_dhcp_client(cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        """
        Update the DHCP version for a specific network interface in the database.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_version (DHCPVersion): The updated DHCP version (DHCP_V4 or DHCP_V6).

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.

        This method attempts to update the DHCP version for a network interface in the database. If the update is successful,
        it returns True (STATUS_OK). If there's an issue during the update, it returns False (STATUS_NOK) and logs an error
        message with the reason for the failure.

        Note:
        - The 'dhcp_version' parameter should be of type DHCPVersion, which is an enumeration containing DHCP versions.
        - The 'STATUS_OK' and 'STATUS_NOK' constants represent success and failure, respectively.
        """
        result = cls.rsdb.insert_interface_dhcp_client(interface_name, dhcp_version.value)
        if result.status:
            cls.log.error(f"Unable to insert {dhcp_version.value} to interface: {interface_name} - reason: {result.reason}")
            return STATUS_NOK
        return STATUS_OK

    def update_db_rename_alias(cls, bus_info: str, initial_interface_name: str, alias_interface_name: str) -> bool:
        """
        Update or create an alias for an initial interface and check if they match.

        Args:
            initial_interface_name (str): The name of the initial interface.
            alias_interface_name (str): The name of the alias interface.

        Returns:
            bool: STATUS_OK if the alias was successfully updated or created and the names match, STATUS_NOK otherwise.

        """
        alias_result = cls.rsdb.is_initial_interface_alias_exist(initial_interface_name)

        if alias_result.status:
            if alias_result.result['AliasInterface'] == alias_interface_name:
                return STATUS_OK
            else:
                return STATUS_NOK
        
        return cls.rsdb.update_interface_alias(bus_info, initial_interface_name, alias_interface_name).status

    def get_interface_aliases(cls) -> List[dict]:
        """
        Get a list of dictionaries representing interface aliases from the InterfaceAlias table.

        Returns:
            List[dict]: A list of dictionaries containing interface alias information.
                Each dictionary includes the following key-value pairs:
                - 'InterfaceName' (str): The name of the primary network interface.
                - 'AliasInterface' (str): The alias name associated with the primary network interface.
        """
        result_list = cls.rsdb.select_interface_aliases()

        aliases_data = [{'InterfaceName': result.result['InterfaceName'], 'AliasInterface': result.result['AliasInterface']} 
                        for result in result_list if result.status == STATUS_OK]

        return aliases_data

    def db_lookup_interface_alias_exist(cls, initial_interface_name: str, alias_interface_name: str) -> bool:
        """
        Check if an alias exists for the given initial interface and alias name.

        Args:
            initial_interface_name (str): The name of the initial interface.
            alias_interface_name (str): The name of the alias interface.

        Returns:
            bool: True if an alias exists for the initial interface with the provided alias name, False otherwise.
        """
        alias_result = cls.rsdb.is_initial_interface_alias_exist(initial_interface_name)

        return alias_result.status and alias_result.result == alias_interface_name

    def update_db_interface_name(cls, old_interface_name:str, new_interface_name:str) -> bool:
        """
        Update the database with a new name for a network interface.

        This class method delegates the task of updating the interface name to the underlying
        network interface manager's 'update_interface_name' method.

        Args:
            old_interface_name (str): The current name of the network interface to be updated.
            new_interface_name (str): The new name to assign to the network interface.

        Returns:
            bool: True if the update process is successful, False otherwise.
        """        
        return cls.rsdb.update_interface_name(old_interface_name, new_interface_name).status

    def update_db_description(cls, interface_name:str, description:str) -> bool:
        """
        Update the description of an interface in the database.

        Args:
            interface_name (str): The name of the interface to update.
            description (str): The new description to set for the interface.

        Returns:
            bool: STATUS_OK if the update operation is successful, STATUS_NOK otherwise.
        """        
        result = cls.rsdb.update_interface_description(interface_name, description)
        return result.status

    def get_db_interface_names(cls) -> List[str]:
        """
        Get a list of all interface names from the database.

        Returns:
            List[str]: A list containing the names of all interfaces in the database.
        """
        results = cls.rsdb.select_interfaces()

        interfaces = []

        for result in results:
            interfaces.append(result.result['InterfaceName'])

        return interfaces

    def get_interface_details(cls) -> List[dict]:
        """
        Retrieve comprehensive details for all network interfaces defined in the DB.

        Returns:
            List[dict]: A list of dictionaries containing interface details.

        Description:
            This method fetches detailed information for all network interfaces stored in the database.
            The information is organized into a list of dictionaries, each representing the details for an individual interface.

        Structure of Each Dictionary:
            {
                'Interfaces': {
                    'InterfaceName': str,
                    'ShutdownStatus': str,
                    'Description': str,
                },
                'Properties': {
                    'InterfaceType': str,
                    'MacAddress': str,
                    'Duplex': str,
                    'Speed': str,
                    'ProxyArp': str,
                    'DropGratArp': str,
                },
                'Alias': {
                    'InitialInterface': str,
                    'AliasInterface': str,
                }
            }
        """
        
        results = cls.rsdb.select_interface_details()

        interface_details_list = []

        for result in results:
            interface_dict = {
                'Interfaces': {
                    'InterfaceName': result.result.get('InterfaceName', ''),
                    'Description': result.result.get('Description', ''),
                    'ShutDownStatus': result.result.get('ShutdownStatus', ''),
                    
                    'Properties': {
                        'InterfaceType': result.result.get('InterfaceType', ''),
                        'MacAddress': result.result.get('MacAddress', ''),
                        'Duplex': result.result.get('Duplex', ''),
                        'Speed': result.result.get('Speed', ''),
                        'ProxyArp': result.result.get('ProxyArp', ''),
                        'DropGratArp': result.result.get('DropGratuitousArp', ''),
                    },
                    
                    'Alias': {
                        'InitialInterface': result.result.get('InitialInterface', ''),
                        'AliasInterface': result.result.get('AliasInterface', ''),
                    }
                }
            }
         
            interface_details_list.append(interface_dict)

        return interface_details_list
        