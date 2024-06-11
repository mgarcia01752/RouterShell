import logging
import os
import platform
import textwrap
from typing import List

from lib.common.constants import Status
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK, Common
from lib.db.sqlite_db.router_shell_db import RouterShellDB
from lib.db.system_db import SystemDatabase
from lib.network_manager.common.phy import State
from lib.network_manager.common.run_commands import RunCommand

class InvalidSystemConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class SystemConfig(RunCommand):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_CONFIG)
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
            
    def set_banner(self, banner_motd: str) -> bool:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            banner_motd (str): The new banner text.

        Returns:
            bool: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """
        return self.sys_db.set_banner_motd(banner_motd)
    
    def del_banner(self) -> bool:
        """
        Delete the banner Message of the Day (MOTD).

        This method sets the banner MOTD in the system configuration to an empty string, effectively removing any existing banner.

        Returns:
            bool: True if the banner MOTD is successfully deleted, False otherwise.

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

    def set_hostname_from_db(self) -> bool:
        """
        Sets the hostname from the system database.

        Retrieves the hostname from the system configuration and updates it from the database if available.

        Returns:
            bool: STATUS_OK if the hostname is successfully set, STATUS_NOK otherwise.
        """
        host_name = SystemConfig.get_hostname()

        rtn = self.sys_db.set_hostname_from_db()
        if rtn.result:
            host_name = rtn.result

        if SystemConfig().set_hostname(host_name):
            print(f"Error: Failed to set the hostname: {host_name}.")
            return STATUS_NOK

        return STATUS_OK
    
    def set_hostname(self, hostname: str) -> bool:
        """
        Set the system hostname.
        
        This function sets the hostname of the system. Currently, it supports Linux.
        
        Parameters:
        hostname (str): The desired hostname to set.

        Returns:
        bool: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        current_os = platform.system()

        if current_os == "Linux":  

            try:
                # Update /etc/hostname
                with open('/etc/hostname', 'w') as f:
                    f.write(hostname + '\n')

                # Ensure the change is recognized without a reboot
                self.run(['hostname', hostname])
                
                self.log.debug(f"Hostname successfully set to {hostname}")

            except Exception as e:
                self.log.error(f"set_hostname(): Failed to set hostname: {e}")
                return STATUS_NOK
        
        else:
            self.log.error(f"set_hostname(): Setting hostname not supported for OS: {current_os}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_hostname(self) -> str:
        """
        Get the current static hostname using the `hostnamectl --static` command.

        Returns:
            str: The current static hostname.
        """
        hostname = os.uname().nodename
        self.log.debug(f'get_hostname() -> {hostname}')
        return hostname

    def is_telnetd_enabled_via_os(self) -> bool:
        """
        Check if the Telnet server (telnetd) is enabled and running on the system.

        Returns:
            bool: True if the Telnet server is enabled and running, False otherwise.
        """
        # Check if the telnetd service is active
        result_active = self.run(['systemctl', 'is-active', 'telnet.socket'])
        if result_active.stdout.strip() == 'active':
            self.log.debug(f'is_telnetd_enabled_via_os() is ACTIVE')
            return True
        
        # Alternatively, check if the telnetd service is enabled
        result_enabled = self.run(['systemctl', 'is-enabled', 'telnet.socket'])
        if result_enabled.stdout.strip() == 'enabled':
            self.log.debug(f'is_telnetd_enabled_via_os() is ENABLE')
            return True
        
        self.log.debug(f'is_telnetd_enabled_via_os() is DISABLE')
        return False

    def set_telnetd_status(self, status: Status) -> bool:
        # Define the path to the Telnet configuration file
        telnet_config_file = '/etc/xinetd.d/telnet'

        # Define the command to restart the Telnet service
        restart_command = ['systemctl', 'restart', 'xinetd']

        # Define the sed command based on the provided status
        disable_status = 'yes' if status == Status.DISABLE else 'no'
        sed_command = ['sed', '-i', 's/disable.*$/disable         = {}/'.format(disable_status), telnet_config_file]

        _ = self.run(sed_command)
        if _.exit_code:
            raise Exception(f'Failed to modify: {telnet_config_file}')
        
        _ = self.run(restart_command)
        if _.exit_code:
            raise Exception(f'Failed to set {restart_command}')
        
        self.sys_db.set_telnet_server_status(status)

        return STATUS_OK

    def get_telnetd_status(self) -> bool:
        """
        Retrieve the current status of the Telnet server.

        Returns:
            bool: True if the Telnet server is enabled, False otherwise.
        """
        status = self.sys_db.get_telnet_server_status()
        self.log.debug(f'get_telnetd_status() -> {status}')
        return status

    def get_ssh_server_status(self) -> bool:
        """
        Retrieve the current status of the SSH server.

        Returns:
            bool: True if the SSH server is enabled, False otherwise.
        """
        status = self.sys_db.get_ssh_server_status()
        self.log.debug(f'get_ssh_server_status() -> {status}')
        return status
