import logging
from typing import List
from lib.common.constants import STATUS_OK, STATUS_NOK

from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.network_manager.network_manager import InterfaceType

class RouterConfiguration:

    CONFIG_MSG_START='; RouterShell Configuration'
    LINE_BREAK = "\n"
    
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

    def get_running_configuration(self, verbose: bool = False, indent: int = 1) -> List[str]:
        """
        Generate the running configuration for the router CLI.

        Returns:
            List[str]: List of CLI commands representing the running configuration.
        """
        
        cli_commands = []

        # Add configuration message start and section break
        cli_commands.extend([self.CONFIG_MSG_START])
        cli_commands.extend([self.LINE_BREAK])

        # Enter configuration mode
        cli_commands.extend(['enable', 'configure terminal'])
        cli_commands.extend([self.LINE_BREAK])

        # Generate CLI commands for global settings
        global_settings_cmds = self._get_global_settings()
        cli_commands.extend(global_settings_cmds)
        cli_commands.extend([self.LINE_BREAK])

        # Generate CLI commands for interface settings
        interface_settings_cmds = self._get_interface_settings()
        cli_commands.extend(interface_settings_cmds)
        cli_commands.extend([self.LINE_BREAK])

        # Generate CLI commands for access control list
        acl_cmds = self._get_access_control_list()
        cli_commands.extend(acl_cmds)

        return cli_commands

    def _get_global_bridge_config(self, indent: int = 1) -> List[str]:
        """
        Generate CLI commands for global bridge configuration.

        Args:
            indent (int, optional): The number of spaces to indent each line. Defaults to 1.

        Returns:
            List[str]: List of CLI commands for global bridge configuration.
        """
        status, bridge_info_results = self.rcdb.get_bridge_configuration()

        if status:
            return []

        bridge_cmd_lines = []

        for bridge_config in bridge_info_results:
            bridge_cmd_lines.extend(
                ' ' * indent + line if i != 0 and i != len(bridge_config.values()) else line
                for i, line in enumerate(filter(None, bridge_config.values()))
            )

        # Place 'end' outside the loop to avoid indentation
        bridge_cmd_lines.append('end')
        bridge_cmd_lines.extend([self.LINE_BREAK])

        return bridge_cmd_lines

    def _get_global_vlan_config(self, indent: int = 1) -> List[str]:
        """
        Generate CLI commands for global VLAN configuration.

        Args:
            indent (int, optional): The number of spaces to indent each line. Defaults to 1.

        Returns:
            List[str]: List of CLI commands for global VLAN configuration.
        """
        status, vlan_info_results = self.rcdb.get_vlan_configuration()

        if status:
            return []

        vlan_cmd_lines = []

        for vlan_config in vlan_info_results:
            vlan_cmd_lines.extend(
                ' ' * indent + line if i != 0 and i != len(vlan_config.values()) else line
                for i, line in enumerate(filter(None, vlan_config.values()))
            )

        # Place 'end' outside the loop to avoid indentation
        vlan_cmd_lines.append('end')
        vlan_cmd_lines.extend([self.LINE_BREAK])

        return vlan_cmd_lines

    def _get_rename_interface_config(self) -> List[str]:
        """
        Generate CLI commands for renaming interface configurations.

        Returns:
            List[str]: List of CLI commands for renaming interface configurations.
        """
        rename_cmd_config_lines = []
        
        status, results = self.rcdb.get_interface_rename_configuration()
        
        if status == STATUS_OK:
            for result in results:
                rename_cmd_setting = result.get('RenameInterfaceConfig')
                rename_cmd_config_lines.append(rename_cmd_setting)
                    
        return rename_cmd_config_lines

    def _get_global_settings(self) -> List[str]:
        """
        Generate CLI commands for global settings.

        Returns:
            List[str]: List of CLI commands for global settings.
        """
        
        global_settings_cmds = []

        global_settings_cmds.extend(self._get_global_bridge_config())
        global_settings_cmds.extend(self._get_global_vlan_config())
        global_settings_cmds.extend(self._get_rename_interface_config())

        return global_settings_cmds

    def _get_interface_settings(self, indent: int = 1) -> List[str]:
        """
        Generate CLI commands for interface settings.

        Returns:
            List[str]: List of CLI commands for interface settings.
        """
        interface_cmds = []

        # Get a list of Ethernet interface names
        ethernet_interfaces = self.rcdb.get_interface_name_list(InterfaceType.ETHERNET)

        # Define values outside the loop
        interface_cmd_lines = []

        for if_name in ethernet_interfaces:
            self.log.debug(f'Interface: {if_name}')

            # Get configuration for the current interface
            status, if_config = self.rcdb.get_interface_configuration(if_name)

            if status:
                self.log.debug(f"Unable to get config for interface: {if_name}")
                continue
            
            status, if_ip_addr_config = self.rcdb.get_interface_ip_address_configuration(if_name)
            
            status, if_ip_static_arp_config = self.rcdb.get_interface_ip_static_arp_configuration(if_name)

            # Indent the lines excluding the first and last lines
            interface_cmd_lines.extend(' ' * indent + line if i != 0 and i != len(if_config.values()) - 1 else line
                                    for i, line in enumerate(filter(None, if_config.values())))

            for ip_addr_config in if_ip_addr_config:
                interface_cmd_lines.extend(' ' * indent + line for line in filter(None, ip_addr_config.values()))

            for ip_static_arp_config in if_ip_static_arp_config:
                interface_cmd_lines.extend(' ' * indent + line for line in filter(None, ip_static_arp_config.values()))

            interface_cmd_lines.append('end')
            
            interface_cmd_lines.extend([self.LINE_BREAK])

            self.log.debug(f'Interface-Config: {interface_cmd_lines}')

        # Append other interface commands
        interface_cmds.extend(interface_cmd_lines)

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
