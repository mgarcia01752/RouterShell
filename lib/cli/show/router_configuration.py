import datetime
import logging
import os
import shutil
from typing import List
from lib.common.constants import STATUS_OK, STATUS_NOK, ROUTER_CONFIG_DIR

from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.db.system_db import SystemDatabase
from lib.network_services.common.network_ports import NetworkPorts
from lib.system.system_call import SystemCall

class RouterConfiguration:

    REMARK_SYMBOL = '!'
    
    CONFIG_MSG_START=f'{REMARK_SYMBOL} RouterShell Configuration'
    STARTUP_CONFIG_FILE = f"{ROUTER_CONFIG_DIR}/startup-config.cfg"
    LINE_BREAK = ""
    
    def __init__(self, args=None):
        """
        Initialize the RouterConfiguration instance.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ROUTER_CONFIG)
        self.rcdb = RouterConfigurationDatabase()
    
    def remark_comment(self, comment: str) -> str:
        """
        Formats a comment string with the configured remark symbol.

        This method takes a comment string and formats it by prepending the 
        configured remark symbol defined in RouterConfiguration.

        Args:
            comment (str): The comment to be formatted.

        Returns:
            str: The formatted comment string with the remark symbol.
        """
        return f'{RouterConfiguration.REMARK_SYMBOL} {comment}'
        
    def copy_running_configuration_to_startup_configuration(self, args=None):
        """
        Copy the running configuration to the startup configuration.
        """
        startup_config_file = f"{ROUTER_CONFIG_DIR}/startup-config.cfg"

        # Add timestamp component to the backup filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_config_file = f"{ROUTER_CONFIG_DIR}/startup-config-backup-{timestamp}.cfg"

        # Check if the startup configuration file exists
        if os.path.exists(startup_config_file):
            # Create a backup of the existing startup configuration file
            shutil.copy2(startup_config_file, backup_config_file)
            self.log.debug(f"Backup of startup configuration created: {backup_config_file}")

        # Save the new running configuration to the startup configuration file
        running_config = self.get_running_configuration()
        with open(startup_config_file, 'w') as file:
            file.write('\n'.join(running_config))

        self.log.debug(f"Running configuration copied to startup configuration: {startup_config_file}")
                
    def get_running_configuration(self, verbose: bool = False, indent: int = 1) -> List[str]:
        """
        Generate the running configuration for the router CLI.

        Returns:
            List[str]: List of CLI commands representing the running configuration.
        """
        
        cmd_lines = []

        # Add configuration message start and section break
        cmd_lines.extend([self.LINE_BREAK])  
        cmd_lines.extend([self.CONFIG_MSG_START])
        cmd_lines.extend([self.LINE_BREAK])        

        # Enter configuration mode
        cmd_lines.extend(['enable', 'configure terminal'])
        cmd_lines.extend([self.LINE_BREAK])
        
        cmd_lines.extend(self._get_hostname())
        cmd_lines.extend([self.LINE_BREAK])
        
        cmd_lines.extend(self._get_banner())

        cmd_lines.extend(self._get_system_servers())
        
        # Generate CLI commands for global settings
        global_settings_cmds = self._get_global_settings()
        cmd_lines.extend(global_settings_cmds)

        # Generate CLI commands for interface settings
        interface_settings_cmds = self._get_interface_settings()
        cmd_lines.extend(interface_settings_cmds)

        # Generate CLI commands for access control list
        acl_cmds = self._get_access_control_list()
        cmd_lines.extend(acl_cmds)

        cmd_lines.append('end')
        
        return cmd_lines

    def _get_global_settings(self) -> List[str]:
            """
            Generate CLI commands for global settings.

            Returns:
                List[str]: List of CLI commands for global settings.
            """
            
            cmd_lines = []

            cmd_lines.extend(self._get_global_rename_interface_config())
            cmd_lines.extend(self._get_global_bridge_config())
            cmd_lines.extend(self._get_global_vlan_config())
            cmd_lines.extend(self._get_global_nat_config())
            cmd_lines.extend(self._get_global_wifi_policy())
            cmd_lines.extend(self._get_global_dhcp_server_config())

            return cmd_lines

    def _get_global_dhcp_server_config(self, indent: int = 1) -> List[str]:
        """
        Generate CLI commands for global DHCP server configuration based on retrieved information.

        Args:
            indent (int, optional): The number of spaces to use for indentation in the generated commands. Defaults to 1.

        Returns:
            List[str]: A list of CLI commands representing global DHCP server configuration.
            
        Note:
        - This method retrieves DHCP server configuration information using the `get_dhcp_server_configuration` method.
        - The generated CLI commands are structured and indented based on the specified indent parameter.
        - If the retrieval of DHCP server configuration information fails, an empty list is returned.
        - The 'end' command is added at the end of the generated commands to denote the completion of configuration.

        """
        status, dhcp_server_info_results = self.rcdb.get_dhcp_server_configuration()

        if status == STATUS_NOK:
            self.log.debug('No DHCP-Server configuration found')
            return []

        cmd_lines = []

        for dhcp_server_config in dhcp_server_info_results:
            cmd_lines.extend(
                ' ' * indent + line if i != 0 and i != len(dhcp_server_config.values()) else line
                for i, line in enumerate(filter(None, dhcp_server_config.values()))
            )
            
            cmd_lines.append('end')
            cmd_lines.append(self.LINE_BREAK)
            
        return cmd_lines
     
    def _get_global_bridge_config(self, indent: int = 1) -> List[str]:
        """
        Generate CLI commands for global bridge configuration.

        Args:
            indent (int, optional): The number of spaces to indent each line. Defaults to 1.

        Returns:
            List[str]: List of CLI commands for global bridge configuration.
        """
        status, bridge_info_results = self.rcdb.get_bridge_configuration()

        if status == STATUS_NOK:
            return []

        cmd_lines = []

        for bridge_config in bridge_info_results:
            cmd_lines.extend([self.LINE_BREAK])
            cmd_lines.extend(
                ' ' * indent + line if i != 0 and i != len(bridge_config.values()) else line
                for i, line in enumerate(filter(None, bridge_config.values()))
            )

        if cmd_lines:
            cmd_lines.append('end')
            cmd_lines.extend([self.LINE_BREAK])

        return cmd_lines

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

        cmd_lines = []

        for vlan_config in vlan_info_results:
            cmd_lines.extend([self.LINE_BREAK])
            cmd_lines.extend(
                ' ' * indent + line if i != 0 and i != len(vlan_config.values()) else line
                for i, line in enumerate(filter(None, vlan_config.values()))
            )

        if cmd_lines:
            cmd_lines.append('end')
            cmd_lines.extend([self.LINE_BREAK])

        return cmd_lines

    def _get_global_rename_interface_config(self) -> List[str]:
        """
        Generate CLI commands for renaming interface configurations based on the database.

        Returns:
            List[str]: A list of CLI commands for renaming interface configurations.
        """
        cmd_lines = []

        status, results = self.rcdb.get_interface_rename_configuration()

        if status == STATUS_OK:
            for result in results:
                cmd_setting = result.get('RenameInterfaceConfig')
                cmd_lines.append(cmd_setting)
            
            return cmd_lines
        
        else:
            self.log.error("Failed to retrieve interface rename configurations.")
            return []

    def _get_global_nat_config(self) -> List[str]:
        """
        Get the global NAT configuration from the database.

        Returns:
        List[str]: A list of global NAT pool names.
        """
        cmd_lines = []

        status, results = self.rcdb.get_nat_configuration()
        self.log.debug(f"_get_global_nat_config() -> {results}")

        if status == STATUS_OK:
            for result in results:
                cmd_lines.extend([self.LINE_BREAK])
                cmd_setting = result.get('IpNatPoolName')
                cmd_lines.append(cmd_setting)
            cmd_lines.append(self.LINE_BREAK)
            return cmd_lines
        
        else:
            self.log.debug("Failed to retrieve global NAT configurations.")
            return []
         
    def _get_interface_settings(self, indent: int = 1) -> List[str]:
        """
        Generate CLI commands for interface settings.

        Returns:
            List[str]: List of CLI commands for interface settings.
        """
        cmd_lines = []

        interface = self.rcdb.get_interface_name_list()

        interface_cmd_lines = []

        for interface_name in interface:
            
            start_temp_interface_cmd_lines = []
            temp_interface_cmd_lines = []
            
            self.log.debug(f'Interface: {interface_name}')

            status, if_config = self.rcdb.get_interface_configuration(interface_name)

            if status:
                self.log.debug(f"Unable to get config for interface: {interface_name}")
                continue
            
            start_temp_interface_cmd_lines.extend(' ' * indent + line if i != 0 and i != len(if_config.values()) - 1 else line
                                                    for i, line in enumerate(filter(None, if_config.values())))
            
            status, if_dhcp_client_config = self.rcdb.get_interface_dhcp_client_configuration(interface_name)
            for _config_line in if_dhcp_client_config:
                temp_interface_cmd_lines.extend(' ' * indent + line for line in filter(None, _config_line.values()))            
            
            status, if_ip_addr_config = self.rcdb.get_interface_ip_address_configuration(interface_name)
            for _config_line in if_ip_addr_config:
                temp_interface_cmd_lines.extend(' ' * indent + line for line in filter(None, _config_line.values()))

            status, if_ip_static_arp_config = self.rcdb.get_interface_ip_static_arp_configuration(interface_name)
            for _config_line in if_ip_static_arp_config:
                temp_interface_cmd_lines.extend(' ' * indent + line for line in filter(None, _config_line.values()))
            
            status, if_ip_sp_acc_vlan_id_config = self.rcdb.get_interface_switchport_access_vlan(interface_name)
            for _config_line in if_ip_sp_acc_vlan_id_config:
                temp_interface_cmd_lines.extend(' ' * indent + line for line in filter(None, _config_line.values()))
                     
            status, if_ds_pol_config = self.rcdb.get_interface_dhcp_server_polices(interface_name)
            for _config_line in if_ds_pol_config:
                temp_interface_cmd_lines.extend(' ' * indent + line for line in filter(None, _config_line.values()))
                            
            status, if_wifi_config = self.rcdb.get_interface_wifi_configuration(interface_name)
            for _config_line in if_wifi_config:
                temp_interface_cmd_lines.extend(' ' * indent + line for line in filter(None, _config_line.values()))                

            start_temp_interface_cmd_lines[1:1] = temp_interface_cmd_lines

            start_temp_interface_cmd_lines.append('end')
            
            start_temp_interface_cmd_lines.extend([self.LINE_BREAK])

            self.log.debug(f'Interface-Config: {start_temp_interface_cmd_lines}')
            
            interface_cmd_lines.extend(start_temp_interface_cmd_lines)

        cmd_lines.extend(interface_cmd_lines)

        return cmd_lines

    def _get_access_control_list(self) -> List[str]:
        """
        Generate CLI commands for access control lists.

        Returns:
            List[str]: List of CLI commands for access control lists.
        """
        cmd_lines = []
        
        return cmd_lines

    def _get_system_telnet_server(self) -> List[str]:
        """
        Generate a list of system server configuration commands based on the Telnet server status.

        Returns:
            List[str]: A list containing the system server configuration command.
        """
        base_cmd = 'system telnet-server port'
        status, result = SystemDatabase().get_telnet_server_status()

        if status:
            self.log.error(f'Error retrieving telnet-server configurations')
            return []
        
        enable = result.get('Enable', False)
        port = result.get('Port', NetworkPorts.TELNET)

        if enable:
            base_cmd = f'{base_cmd} {port}'
        else:
            base_cmd = f'no {base_cmd} {port}'

        return [base_cmd]

    def _get_system_ssh_server(self) -> List[str]:
        """
        Generate a list of system server configuration commands based on the SSH server status.

        Returns:
            List[str]: A list containing the system server configuration command.
        """
        base_cmd = 'system ssh-server port'
        
        # Retrieve the SSH server status from the database
        status, result = SystemDatabase().get_ssh_server_status()
        
        # Check if the status retrieval was successful
        if status == STATUS_NOK:
            self.log.error(f"Error retrieving SSH server configurations")
            return []

        enable = result.get('Enable', False)
        port = result.get('Port', NetworkPorts.SSH)
        
        # Construct the command based on the retrieved status
        if enable:
            base_cmd = f'{base_cmd} {port}'
        else:
            base_cmd = f'no {base_cmd} {port}'

        return [base_cmd]

    def _get_system_servers(self) -> List[str]:
        """
        Generate a list of system server configuration commands based on the statuses of telnet and ssh servers.

        Returns:
            List[str]: A combined list of system server configuration commands.
        """
        cmd_lines = self._get_system_telnet_server()
        cmd_lines.extend(self._get_system_ssh_server())

        return cmd_lines
    
    def _get_banner(self) -> List[str]:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration and split it into a list of strings.

        Returns:
            List[str]: The formatted banner text as a list of strings, where each element represents a line in the banner.
        """
        banner_text = SystemCall().get_banner()
        
        if not banner_text:
            return []

        config_cmd = ['banner motd ^']
        config_cmd.extend(banner_text.split("\n"))
        config_cmd.append('^')

        return config_cmd
    
    def _get_hostname(self) -> List[str]:
        
        hostname = f'hostname {SystemDatabase().get_hostname_db()}'

        return [hostname]

    def _get_global_wifi_policy(self, indent: int=1) -> List[str]:
        """
        Generate CLI commands for WiFi policy configuration.

        Args:
            indent (int, optional): The number of spaces to use for indentation. Defaults to 1.

        Returns:
            List[str]: List of CLI commands for WiFi policy configuration. Each command is indented based on the specified 'indent' parameter.
        """
        cmd_lines = []

        status, wifi_policy_config = self.rcdb.get_wifi_policy_configuration()

        if status == STATUS_OK:

            for wifi_policy, config_data in wifi_policy_config.items():
                
                temp_cmd_line = []
                
                self.log.debug(f'Wifi-Config: {config_data}')
                
                temp_cmd_line.append(config_data.get('WifiPolicyName'))

                wifi_sec_policy_list = config_data.get('WifiSecurityPolicy')

                if isinstance(wifi_sec_policy_list, list):
                    
                    for item in wifi_sec_policy_list:
                        # TODO Add a check for None Values and exit properly
                        ssid_line = " ".join(item.values())
                        temp_cmd_line.append(indent * ' ' + ssid_line)
                        
                temp_cmd_line.append(indent * ' ' + f"{config_data.get('Channel')}")
                temp_cmd_line.append(indent * ' ' + f"{config_data.get('HardwareMode')}")

                cmd_lines.extend(temp_cmd_line)
                cmd_lines.append('end')               
                cmd_lines.append(self.LINE_BREAK)

        return cmd_lines

      