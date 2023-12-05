import logging
from typing import List

from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.network_manager.network_manager import InterfaceType

class RouterConfiguration:

    def __init__(self, args=None):
        """
        Initialize the RouterConfiguration instance.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_CONFIG)
        self.rcdb = RouterConfigurationDatabase()
        

    def copy_running_configuration_to_startup_configuration(self, args=None):
        """
        Copy the running configuration to the startup configuration.
        """
        # Implement the logic for copying configurations if needed
        pass

    def get_running_configuration(self, verbose:bool=False, indent:int=1) -> List[str]:
        """
        Generate the running configuration for the router CLI.

        Returns:
            List[str]: List of CLI commands representing the running configuration.
        """
        cli_commands = ['enable', 'configure terminal']

        # Generate CLI commands for different sections
        cli_commands.extend(self._get_global_settings())
        cli_commands.extend(self._get_interface_settings())
        cli_commands.extend(self._get_access_control_list())

        return cli_commands

    def _get_global_settings(self) -> List[str]:
        """
        Generate CLI commands for global settings.

        Returns:
            List[str]: List of CLI commands for global settings.
        """
        global_settings_cmds = [

        ]

        return global_settings_cmds

    def _get_interface_settings(self) -> List[str]:
        """
        Generate CLI commands for interface settings.

        Returns:
            List[str]: List of CLI commands for interface settings.
        """
        interface_cmds = []

        # Get a list of Ethernet interface names
        ethernet_interfaces = self.rcdb.get_interface_name_list(InterfaceType.ETHERNET)

        # Define values outside the loop
        values = []

        for if_name in ethernet_interfaces:
            self.log.debug(f'Interface: {if_name}')

            # Get configuration for the current interface
            status, if_config = self.rcdb.get_interface_configuration(if_name)

            if status:
                self.log.debug(f"Unable to get config for interface: {if_name}")
                continue

            values.extend(filter(None, if_config.values()))
            values.append('end')
            
            self.log.debug(f'Interface-Config: {values}')

        # Append other interface commands
        interface_cmds.extend(values)

        return interface_cmds

    def _get_access_control_list(self) -> List[str]:
        """
        Generate CLI commands for access control lists.

        Returns:
            List[str]: List of CLI commands for access control lists.
        """
        acl_cmds = [

        ]
        return acl_cmds
