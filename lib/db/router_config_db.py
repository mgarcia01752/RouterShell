import logging
from typing import Dict, List, Tuple

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_manager import InterfaceType

class RouterConfigurationDatabase:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().ROUTER_CONFIG_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()
    
    def get_interface_name_list(cls, interface_type: InterfaceType) -> List[str]:
        """
        Get a list of interface names based on the specified interface type.

        Args:
            interface_type (InterfaceType): The type of interface to filter by.

        Returns:
            List[str]: A list of interface names.
        """
        interface_list = []

        interface_result_list = cls.rsdb.select_interfaces_by_interface_type(interface_type)

        for interface in interface_result_list:
            cls.log.debug(f"get_interface_name_list() -> {interface}")
            if interface.status == STATUS_OK:
                interface_names = interface.result.get('InterfaceName')

                # Ensure interface_names is a list, even if it contains a single value
                if isinstance(interface_names, str):
                    interface_list.append(interface_names)
                elif isinstance(interface_names, list):
                    interface_list.extend(interface_names)

        return interface_list
    
    def get_interface_configuration(cls, interface_name: str) -> Tuple[bool, dict]:
        """
        Get the configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            Tuple[bool, dict]: A tuple containing a boolean indicating the status and a dictionary with the interface configuration.
        """
        if_result = cls.rsdb.select_interface_configuration(interface_name)
        
        cls.log.debug(f'Interface-Base-Config: {if_result}')
        
        return if_result.status, if_result.result

    def get_interface_rename_configuration(cls) -> Tuple[bool, List[Dict]]:
        """
        Retrieve data from the 'RenameInterface' table.

        Returns:
            Tuple[bool, List[Dict]]:
            - A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with data from the 'RenameInterface' table.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
                    with 'InitialInterface' and 'AliasInterface' values.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_interface_rename_configuration()')

        rename_list = []

        rename_result = cls.rsdb.select_interface_rename_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in rename_result):
            error_messages = [result.reason for result in rename_result if result.status]
            cls.log.debug(f"Error retrieving rename-interface-line, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in rename_result:
            rename_list.append(result.result)

        return STATUS_OK, rename_list




