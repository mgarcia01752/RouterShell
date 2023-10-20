import logging
import re

from lib.db.sqlite_db.router_shell_db import Result, RouterShellDatabaseConnector as RSDB
from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_NOK, STATUS_OK

class InterfaceConfigDB:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().INTERFACE_DB)
        
        '''CMD2 DEBUG LOGGING'''
        cls.debug = CGS().DEBUG_INTERFACE_DB
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()  
            
    def interface_exists(cls, interface_name: str) -> Result:
        """
        Check if an interface with the given name exists in the database.

        Args:
            interface_name (str): The name of the interface to check.

        Returns:
            Result: A Result object with the status and row ID of the existing interface.

        Example:
            You can use this method to determine whether a specific interface exists in the database.
            For instance, you might check if 'GigabitEthernet0/1' exists.

        Usage:
            result = interface_exists('GigabitEthernet0/1')
            if result.status:
                print(f"Interface with name '{interface_name}' exists in the database.")
            else:
                print(f"Interface with name '{interface_name}' does not exist.")

        Note:
            - The 'Result' object returned indicates the status of the interface existence.
            - 'status' True means the interface exists, and 'status' False means it does not.
        """
        return cls.rsdb.interface_exists(interface_name)

    def add_interface(cls, interface_name: str, interface_type: str, shutdown_status: bool = True) -> bool:
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
            cls.log.debug(f"add_interface() - Unable to add interface to DB -> {result.result}")
            return STATUS_NOK
        
        return STATUS_OK

    def del_interface(cls, interface_name: str) -> bool:
        """
        Delete an interface from the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to delete.

        Returns:
            bool: STATUS_OK if the deletion was successful, STATUS_OK otherwise.
        """
        result = cls.rsdb.delete_interface(interface_name)
        
        return result.status
 
    def update_shutdown_status(cls, interface_name: str, status: bool) -> bool:
        """
        Update the shutdown status of an interface in the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to update.
            status (bool): The new shutdown status.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_shutdown(interface_name, status)
        return result.status

    def update_duplex_status(cls, interface_name: str, duplex: str) -> bool:
        """
        Update the duplex status of an interface in the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to update.
            duplex (str): The new duplex status.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        result = cls.rsdb.update_interface_duplex(interface_name, duplex)
        return result.status
    
    def update_mac_address(cls, interface_name: str, mac_address: str) -> bool:
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

    def update_speed(cls, interface_name: str, speed: str) -> bool:
        """
        Update the speed setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            speed (str): The speed setting (e.g., '10', '100', '1000', '10000', 'auto').

        Returns:
            bool: STATUS_OK if the speed was successfully updated, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_speed(interface_name, speed)
        return result.status

    def update_ip_address(cls, interface_name, ip_address_mask, secondary=False, negate=False) -> bool:
        """
        Update or delete an IP address setting for an interface.

        Args:
            interface_name (str): The name of the interface.
            ip_address_mask (str): The IP address/mask to update or delete.
            secondary (bool): True if the IP address is secondary, False otherwise.
            negate (bool): True to delete the IP address, False to update.

        Returns:
            bool: bool: STATUS_OK if the speed was successfully updated, STATUS_NOK otherwise.
        """
        if not negate:
            result = cls.rsdb.insert_interface_ip_address(interface_name, ip_address_mask, secondary)
        else:
            result = cls.rsdb.delete_interface_ip_address(interface_name, ip_address_mask)

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
    
    def update_proxy_arp(cls, interface_name: str, status: bool) -> bool:
        """
        Update the Proxy ARP status for a network interface.

        Args:
            interface_name (str): The name of the network interface.
            status (bool): The new Proxy ARP status (True for enabled, False for disabled).

        Returns:
            Result: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_proxy_arp(interface_name, status)
        return result.status

    def update_drop_gratuitous_arp(cls, interface_name: str, status: bool) -> bool:
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
    
    def update_static_arp(cls, interface_name: str, ip_address: str, mac_address: str, encapsulation: str='arpa', negate=False) -> bool:
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
            result = cls.rsdb.insert_interface_static_arp(interface_name, ip_address, mac_address, encapsulation)
        else:
            result = cls.rsdb.delete_interface_ip_address(interface_name, ip_address)

        return result.status

