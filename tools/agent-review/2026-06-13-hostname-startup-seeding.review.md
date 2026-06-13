### Summary
RouterShell no longer renders `hostname None` when the runtime database has no hostname. Startup now seeds a missing hostname value from the operating system without reconfiguring the host, and running configuration output falls back to the OS hostname when needed.

### Modified Files
- src/routershell/lib/system/system_call.py
- src/routershell/lib/system/system_start_up.py
- src/routershell/lib/cli/show/router_configuration.py
- tests/packaging/test_hostname_startup.py
- doc/faq.md
- todo.md

### Commands Executed And Results
- `hostname && hostnamectl --static 2>/dev/null || true && cat /etc/hostname 2>/dev/null || true` → host OS reported `dev01`
- `ROUTERSHELL_DB_FILE=/home/dev01/Projects/RouterShell/.routershell/hostname-trace.db PYTHONPATH=src /opt/routershell/venv/bin/python ...` → traced blank DB hostname as `None`, OS hostname as `dev01`, and DB seed as `dev01`
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_hostname_startup.py -q` → pass, 3 passed
- `/opt/routershell/venv/bin/python -m ruff check src/routershell/lib/system/system_call.py src/routershell/lib/system/system_start_up.py src/routershell/lib/cli/show/router_configuration.py tests/packaging/test_hostname_startup.py` → pass
- `ROUTERSHELL_DB_FILE=<temp>/routershell.db PYTHONPATH=src /opt/routershell/venv/bin/python ...` → pass, running-config hostname output was `hostname dev01` before and after seeding
- `/opt/routershell/venv/bin/python -m pytest -q` → pass, 28 passed
- `/opt/routershell/venv/bin/python -m ruff check .` → pass

### Tests
- `pytest` → pass, 28 passed
- `ruff` → pass, all checks passed

# FILE: src/routershell/lib/system/system_call.py
import logging
import os
import platform
import shutil
import textwrap

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.constants import ETC_HOSTNAME_FILE
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import HostnameText, StatusResult
from routershell.lib.db.system_db import SystemDatabase
from routershell.lib.network_manager.common.run_commands import RunCommand, RunLog
from routershell.lib.system.init_system import InitSystemChecker


class InvalidSystemConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class SystemCall(RunCommand):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_CALL)
        self.arg = arg
        self.sys_db = SystemDatabase()

    def get_banner(self, max_line_length: int=0) -> str:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration.

        Args:
            cls: The RouterShellDB class.
            max_line_length (int): The maximum length for each line in the banner text.

        Returns:
            str: The formatted banner text with lines limited to the specified maximum length.
        """
        result, banner_text = self.sys_db.get_banner_motd()
                
        if result:
            return ""
        
        if max_line_length:
            return textwrap.fill(banner_text, width=max_line_length)

        return banner_text
            
    def set_banner(self, banner_motd: str) -> StatusResult:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            banner_motd (str): The new banner text.

        Returns:
            StatusResult: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """
        return self.sys_db.set_banner_motd(banner_motd)
    
    def del_banner(self) -> StatusResult:
        """
        Delete the banner Message of the Day (MOTD).

        This method sets the banner MOTD in the system configuration to an empty string, effectively removing any existing banner.

        Returns:
            StatusResult: True if the banner MOTD is successfully deleted, False otherwise.

        Example:
            To delete the banner MOTD, you can use the 'del_banner' method as follows:

            >>> result = SystemConfigurator().del_banner()
            >>> if result:
            ...     print("Banner MOTD deleted successfully.")
            ... else:
            ...     print("Failed to delete banner MOTD.")

        Note:
            - This method updates the system configuration using the 'set_banner_motd' method of the underlying 'SystemDatabase' class.
            - The 'set_banner_motd' method returns True if the update is successful, and False otherwise.
        """
        return self.sys_db.set_banner_motd('')

    def set_hostname_from_db(self) -> StatusResult:
        """
        Sets the hostname from the system database if available; otherwise, uses the system configuration.

        Retrieves the hostname from the system database. If the database does not provide a hostname, it falls back to the system configuration.
        Attempts to set the system hostname to the retrieved value.

        Returns:
            StatusResult: STATUS_OK if the hostname is successfully set, STATUS_NOK otherwise.
        """
        host_name = self.sys_db.get_hostname_db()
        self.log.debug(f'set_hostname_from_db() -> Retrieved hostname from DB: {host_name}')
        
        if not host_name:
            host_name = self.get_hostname_os()
            self.log.debug(f'No hostname found in DB, setting hostname: ({host_name}) to DB')
            
            if self.sys_db.set_hostname_db(host_name):
                self.log.error(f"Failed to set the hostname: ({host_name}) to DB")
                return STATUS_NOK
            return STATUS_OK

        if self.set_hostname_os(host_name):
            self.log.error(f"Failed to set the hostname: ({host_name}) via OS")
            return STATUS_NOK

        return STATUS_OK

    def seed_hostname_db_from_os(self) -> StatusResult:
        """
        Seed the RouterShell hostname database value from the operating system.

        The database starts with an empty hostname on a fresh install. This
        method records the current OS hostname only when RouterShell does not
        already have a configured hostname, avoiding unnecessary host
        reconfiguration during startup.

        Returns:
            StatusResult: STATUS_OK if the database already has a hostname or
                is seeded successfully, STATUS_NOK otherwise.
        """
        host_name = self.sys_db.get_hostname_db()
        if host_name:
            return STATUS_OK

        host_name = self.get_hostname_os()
        if not host_name:
            self.log.error("Unable to seed hostname DB because OS hostname is empty")
            return STATUS_NOK

        if self.sys_db.set_hostname_db(host_name):
            self.log.error(f"Failed to seed hostname DB from OS hostname: ({host_name})")
            return STATUS_NOK

        return STATUS_OK
    
    def set_hostname_os(self, hostname: HostnameText) -> StatusResult:
        """
        Set the system hostname.
        
        This function sets the hostname of the system. Currently, it supports Linux.
        
        Parameters:
        hostname (str): The desired hostname to set.

        Returns:
        StatusResult: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        current_os = platform.system()

        if current_os == "Linux":
            try:
                if InitSystemChecker().is_sysv():
                    # Set the hostname permanently.
                    with open(ETC_HOSTNAME_FILE, 'w') as f:
                        f.write(hostname + '\n')

                    # Check if the hostname command is available
                    if not shutil.which('hostname'):
                        self.log.fatal(f"hostname command not found on the system, unable to set hostname: {hostname}")
                        return STATUS_NOK

                    # Set the hostname temporarily until the next reboot
                    result = self.run(['hostname', hostname])
                    if result.exit_code:
                        self.log.error(f"Failed to set hostname (SysV): {result}, reason: {result.stderr}")
                        return STATUS_NOK

                elif InitSystemChecker().is_systemd():
                    # Set the hostname permanently using hostnamectl
                    result = self.run(['hostnamectl', 'set-hostname', hostname])
                    if result.exit_code:
                        self.log.error(f"Failed to set hostname (systemd): {result}, reason: {result.stderr}")
                        return STATUS_NOK

                else:
                    self.log.error("set_hostname_os(): Unsupported init system.")
                    return STATUS_NOK

                self.log.debug(f"set_hostname_os() -> Hostname successfully set to {hostname}")
                return STATUS_OK

            except Exception as e:
                self.log.error(f"set_hostname_os(): Failed to set hostname: {e}")
                return STATUS_NOK

        else:
            self.log.error(f"set_hostname_os(): Setting hostname not supported for OS: {current_os}")
            return STATUS_NOK
        
    def get_hostname_os(self) -> str:
        """
        Get the current static hostname using the `hostnamectl --static` command.

        Returns:
            str: The current static hostname.
        """
        hostname = os.uname().nodename
        self.log.debug(f'get_hostname() -> {hostname}')
        return hostname
    
    def get_run_log(self) -> list[str]:
        """
        Retrieve the run log from the RunLog utility class.

        Returns:
            list[str]: A list of strings representing each line of the run log file.

        Example:
            >>> instance = SomeOtherClass()
            >>> log_contents = instance.get_run_log()
            >>> for line in log_contents:
            >>>     print(line)
        """
        return RunLog().get_run_log()
    

# FILE: src/routershell/lib/system/system_start_up.py
import logging

from routershell.lib.cli.base.copy_start_run import CopyStartRun
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.system.system_call import SystemCall


class SystemStartUp(Interface):
    """
    Class for managing system startup procedures.

    Inherits from Interface.
    """
    def __init__(self):
        """
        Initializes the SystemStartUp class.
        """
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_START_UP)

        if not self.fetch_db_interface_names():
            self.update_interface_db_from_os()
            
        SystemCall().seed_hostname_db_from_os()
            
        self.set_os_rename_interface()
        
        self.log.debug('Loading........')
        CopyStartRun().read_start_config()
            
class SystemShutDown(RunCommand):    
    """
    Class for managing system shutdown procedures.

    Inherits from RunCommand.
    """
    def __init__(self):
        """
        Initializes the SystemShutDown class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_START_UP)
            
class SystemReset(Interface):
    """
    Class for resetting system settings.

    Inherits from Interface.
    """
    def __init__(self):
        """
        Initializes the SystemReset class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_RESET)
        
    def database(self):
        """
        Resets the system database.

        Reverts some settings in the OS when clearing the database.
        """
        # Flush interfaces
        Interface().flush_interfaces()
                
        # Revert Interfaces back to the original interface name
        Interface().set_os_rename_interface(reverse=True)

class SystemFactoryReset:
    def __init__(self):
        """
        Initializes the SystemFactoryReset class.
        """
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_INIT)

        RouterShellDB().reset_database()
        
        #Build Initial DB Entries based on Interface found on system
        Interface().update_interface_db_from_os()
        
        #Take factory-startup-config and configure router    
        CopyStartRun().read_start_config('factory-startup.cfg')

# FILE: src/routershell/lib/cli/show/router_configuration.py
import datetime
import logging
import os
import shutil

from routershell.lib.common.constants import ROUTER_CONFIG_DIR, STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.db.router_config_db import RouterConfigurationDatabase
from routershell.lib.db.system_db import SystemDatabase
from routershell.lib.network_services.common.network_ports import NetworkPorts
from routershell.lib.system.system_call import SystemCall


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
                
    def get_running_configuration(self, verbose: bool = False, indent: int = 1) -> list[str]:
        """
        Generate the running configuration for the router CLI.

        Returns:
            list[str]: list of CLI commands representing the running configuration.
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

    def _get_global_settings(self) -> list[str]:
            """
            Generate CLI commands for global settings.

            Returns:
                list[str]: list of CLI commands for global settings.
            """
            
            cmd_lines = []

            cmd_lines.extend(self._get_global_rename_interface_config())
            cmd_lines.extend(self._get_global_bridge_config())
            cmd_lines.extend(self._get_global_vlan_config())
            cmd_lines.extend(self._get_global_nat_config())
            cmd_lines.extend(self._get_global_wifi_policy())
            cmd_lines.extend(self._get_global_dhcp_server_config())

            return cmd_lines

    def _get_global_dhcp_server_config(self, indent: int = 1) -> list[str]:
        """
        Generate CLI commands for global DHCP server configuration based on retrieved information.

        Args:
            indent (int, optional): The number of spaces to use for indentation in the generated commands. Defaults to 1.

        Returns:
            list[str]: A list of CLI commands representing global DHCP server configuration.
            
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
     
    def _get_global_bridge_config(self, indent: int = 1) -> list[str]:
        """
        Generate CLI commands for global bridge configuration.

        Args:
            indent (int, optional): The number of spaces to indent each line. Defaults to 1.

        Returns:
            list[str]: list of CLI commands for global bridge configuration.
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

    def _get_global_vlan_config(self, indent: int = 1) -> list[str]:
        """
        Generate CLI commands for global VLAN configuration.

        Args:
            indent (int, optional): The number of spaces to indent each line. Defaults to 1.

        Returns:
            list[str]: list of CLI commands for global VLAN configuration.
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

    def _get_global_rename_interface_config(self) -> list[str]:
        """
        Generate CLI commands for renaming interface configurations based on the database.

        Returns:
            list[str]: A list of CLI commands for renaming interface configurations.
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

    def _get_global_nat_config(self) -> list[str]:
        """
        Get the global NAT configuration from the database.

        Returns:
        list[str]: A list of global NAT pool names.
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
         
    def _get_interface_settings(self, indent: int = 1) -> list[str]:
        """
        Generate CLI commands for interface settings.

        Returns:
            list[str]: list of CLI commands for interface settings.
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

    def _get_access_control_list(self) -> list[str]:
        """
        Generate CLI commands for access control lists.

        Returns:
            list[str]: list of CLI commands for access control lists.
        """
        cmd_lines = []
        
        return cmd_lines

    def _get_system_telnet_server(self) -> list[str]:
        """
        Generate a list of system server configuration commands based on the Telnet server status.

        Returns:
            list[str]: A list containing the system server configuration command.
        """
        base_cmd = 'system telnet-server port'
        status, result = SystemDatabase().get_telnet_server_status()

        if status:
            self.log.error('Error retrieving telnet-server configurations')
            return []
        
        enable = result.get('Enable', False)
        port = result.get('Port', NetworkPorts.TELNET)

        if enable:
            base_cmd = f'{base_cmd} {port}'
        else:
            base_cmd = f'no {base_cmd} {port}'

        return [base_cmd]

    def _get_system_ssh_server(self) -> list[str]:
        """
        Generate a list of system server configuration commands based on the SSH server status.

        Returns:
            list[str]: A list containing the system server configuration command.
        """
        base_cmd = 'system ssh-server port'
        
        # Retrieve the SSH server status from the database
        status, result = SystemDatabase().get_ssh_server_status()
        
        # Check if the status retrieval was successful
        if status == STATUS_NOK:
            self.log.error("Error retrieving SSH server configurations")
            return []

        enable = result.get('Enable', False)
        port = result.get('Port', NetworkPorts.SSH)
        
        # Construct the command based on the retrieved status
        if enable:
            base_cmd = f'{base_cmd} {port}'
        else:
            base_cmd = f'no {base_cmd} {port}'

        return [base_cmd]

    def _get_system_servers(self) -> list[str]:
        """
        Generate a list of system server configuration commands based on the statuses of telnet and ssh servers.

        Returns:
            list[str]: A combined list of system server configuration commands.
        """
        cmd_lines = self._get_system_telnet_server()
        cmd_lines.extend(self._get_system_ssh_server())

        return cmd_lines
    
    def _get_banner(self) -> list[str]:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration and split it into a list of strings.

        Returns:
            list[str]: The formatted banner text as a list of strings, where each element represents a line in the banner.
        """
        banner_text = SystemCall().get_banner()
        
        if not banner_text:
            return []

        config_cmd = ['banner motd ^']
        config_cmd.extend(banner_text.split("\n"))
        config_cmd.append('^')

        return config_cmd
    
    def _get_hostname(self) -> list[str]:
        
        hostname = SystemDatabase().get_hostname_db() or SystemCall().get_hostname_os()

        return [f'hostname {hostname}']

    def _get_global_wifi_policy(self, indent: int=1) -> list[str]:
        """
        Generate CLI commands for WiFi policy configuration.

        Args:
            indent (int, optional): The number of spaces to use for indentation. Defaults to 1.

        Returns:
            list[str]: list of CLI commands for WiFi policy configuration. Each command is indented based on the specified 'indent' parameter.
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

      

# FILE: tests/packaging/test_hostname_startup.py
from __future__ import annotations

from pathlib import Path


def test_seed_hostname_db_from_os_populates_blank_database(monkeypatch, tmp_path: Path) -> None:
    from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, STATUS_OK
    from routershell.lib.common.singleton import Singleton
    from routershell.lib.db.interface_db import InterfaceDatabase
    from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
    from routershell.lib.db.system_db import SystemDatabase
    from routershell.lib.system.system_call import SystemCall

    monkeypatch.setenv(ROUTER_SHELL_DB_FILE_ENV, str(tmp_path / "routershell.db"))
    Singleton._instances.pop(RouterShellDB, None)
    RouterShellDB.connection = None
    RouterShellDB.connection_created = False
    SystemDatabase.rsdb = RouterShellDB()
    InterfaceDatabase.rsdb = SystemDatabase.rsdb

    system_call = SystemCall()
    monkeypatch.setattr(system_call, "get_hostname_os", lambda: "dev01")

    assert system_call.sys_db.get_hostname_db() is None
    assert system_call.seed_hostname_db_from_os() == STATUS_OK
    assert system_call.sys_db.get_hostname_db() == "dev01"


def test_startup_seeds_hostname_without_reconfiguring_existing_hostname(monkeypatch) -> None:
    from routershell.lib.common.constants import STATUS_OK
    from routershell.lib.system.system_start_up import SystemStartUp

    seed_calls = []

    class FakeSystemCall:
        def seed_hostname_db_from_os(self) -> bool:
            seed_calls.append(True)
            return STATUS_OK

    monkeypatch.setattr(SystemStartUp, "fetch_db_interface_names", lambda self: ["enp1s0"])
    monkeypatch.setattr(SystemStartUp, "set_os_rename_interface", lambda self: STATUS_OK)
    monkeypatch.setattr(
        "routershell.lib.system.system_start_up.SystemCall",
        lambda: FakeSystemCall(),
    )
    monkeypatch.setattr(
        "routershell.lib.system.system_start_up.CopyStartRun",
        lambda: type("FakeCopyStartRun", (), {"read_start_config": lambda self: STATUS_OK})(),
    )

    SystemStartUp()

    assert seed_calls == [True]


def test_running_config_hostname_falls_back_to_os_hostname(monkeypatch) -> None:
    from routershell.lib.cli.show.router_configuration import RouterConfiguration

    class FakeSystemDatabase:
        def get_hostname_db(self) -> None:
            return None

    class FakeSystemCall:
        def get_hostname_os(self) -> str:
            return "dev01"

    monkeypatch.setattr(
        "routershell.lib.cli.show.router_configuration.SystemDatabase",
        lambda: FakeSystemDatabase(),
    )
    monkeypatch.setattr(
        "routershell.lib.cli.show.router_configuration.SystemCall",
        lambda: FakeSystemCall(),
    )

    assert RouterConfiguration()._get_hostname() == ["hostname dev01"]

# FILE: doc/faq.md
# RouterShell FAQ

## Install fails with setuptools InvalidConfigError

If `sudo ./install/install.sh --development` fails while getting editable
build requirements and reports this error:

```text
setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions
```

Update RouterShell to a version whose `pyproject.toml` uses the SPDX
`license = "Apache-2.0"` expression without deprecated license classifiers,
then rerun the installer:

```bash
sudo ./install/install.sh --development
```

This error is raised by newer setuptools releases during package metadata
validation.

## VSCode reports unresolved RouterShell imports

If VSCode or Pylance reports unresolved imports for `routershell` or
`tools.release.qa_checker`, reload the VSCode window after opening the
RouterShell workspace. The workspace settings select the installed development
interpreter at `/opt/routershell/venv/bin/python` and add the project `src`
layout plus release tooling paths to Python analysis.

If command-line Pyright is also needed, reinstall development extras:

```bash
/opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

If VSCode reports a Pylint `E0401:import-error` for a RouterShell module such
as `routershell.lib.cli.base.clear_mode`, make sure the workspace is using the
RouterShell interpreter and reload VSCode. The workspace settings configure the
Pylint extension to run from `/opt/routershell/venv/bin/python` with the
project `src` layout on the import path.

If the Pylint extension reports that Pylint is missing, refresh development
dependencies in the installer-created virtual environment:

```bash
sudo /opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

## RouterShell fails with unable to open database file

If `routershell` exits during startup with this error:

```text
RouterShellDB - ERROR - Error: unable to open database file
AttributeError: 'NoneType' object has no attribute 'cursor'
```

the launcher is missing a writable `ROUTERSHELL_DB_FILE` setting or is using an
older install. Reinstall RouterShell so the launcher-loaded env file gets any
missing required keys and the installed package receives the current DB path
code:

```bash
sudo ./install/install.sh --development
```

For local/development installs, the default database path is
`.routershell/routershell.db` under the project root. For production installs,
the default path is `/var/lib/routershell/routershell.db`.

## Interface database is empty after install

`routershell` should seed the interface database during startup when the
database has no interface records. Start the CLI normally:

```bash
routershell
```

Then verify the discovered interfaces:

```text
show interface database
```

If the database is still empty, confirm that the launcher-loaded environment
file defines a writable `ROUTERSHELL_DB_FILE` path and reinstall with the
current installer.

## Running configuration shows hostname None

If `show running-config` displays this line:

```text
hostname None
```

the runtime database is missing a RouterShell hostname value. Current
RouterShell startup seeds the hostname database value from the operating system
when it is blank, and running configuration output falls back to the OS
hostname instead of rendering `None`.

Start RouterShell normally, then check the running configuration again:

```bash
routershell
```

```text
show running-config
```

# FILE: todo.md
# RouterShell TODO

- Keep install troubleshooting notes current when installer errors are fixed.
- Keep IDE import troubleshooting notes current when workspace settings change.
- Keep runtime database troubleshooting notes current when DB path handling changes.
- Keep runtime display troubleshooting notes current when CLI output renders missing DB values.
