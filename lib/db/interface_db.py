import logging
import re

from lib.db.router_shell_db import Result, RouterShellDatabaseConnector as RSDB
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
            
    def interface_exists(cls, interface_name:str) -> Result:
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
 
    def update_shutdown_status(cls, interface_name: str, shutdown_status: bool) -> bool:
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
            bool: True (STATUS_OK) if the speed was successfully updated, False (STATUS_NOK) otherwise.
        """
        result = cls.rsdb.update_interface_speed(interface_name, speed)
        return result.status


    def update_ip_address(cls, interface_name:str, ip_address_mask:str, secondary:bool) -> bool:
        '''Bool: STATUS_OK/STATUS_NOK'''
        pass        
