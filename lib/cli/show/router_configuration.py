import logging
from typing import Dict, List
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

class RouterConfiguration:

    def __init__(self, args=None):
        """
        Initialize the RouterConfiguration instance.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_CONFIG)

    def copy_running_configuration_to_startup_configuration(self, args=None):
        """
        Copy the running configuration to the startup configuration.
        """
        # Implement the logic for copying configurations if needed
        pass

    def get_running_configuration(self, args=None) -> Dict:
        """
        Generate the running configuration for the router CLI.

        Returns:
            Dict: A dictionary representing the running configuration.
        """
        cli_commands = ['enable', 
                        'configuration terminal']

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
            # Add commands for global settings, NAT, VLAN, etc.
            'global setting command',
            'global NAT command',
            'global VLAN command',
        ]
        return global_settings_cmds

    def _get_interface_settings(self) -> List[str]:
        """
        Generate CLI commands for interface settings.

        Returns:
            List[str]: List of CLI commands for interface settings.
        """
        interface_cmds = [
            # Add commands for interfaces (loopback, ethernet, wifi)
            'interface loopback command',
            'interface ethernet command',
            'interface wifi command',
        ]
        return interface_cmds

    def _get_access_control_list(self) -> List[str]:
        """
        Generate CLI commands for access control lists.

        Returns:
            List[str]: List of CLI commands for access control lists.
        """
        acl_cmds = [
            # Add commands for access control lists
            'access control list command',
        ]
        return acl_cmds
