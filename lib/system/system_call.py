import logging
import os
import platform
import textwrap
from typing import List

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.db.system_db import SystemDatabase
from lib.network_manager.common.run_commands import RunCommand, RunLog

class InvalidSystemConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class SystemCall(RunCommand):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_CALL)
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
        Sets the hostname from the system database if available; otherwise, uses the system configuration.

        Retrieves the hostname from the system database. If the database does not provide a hostname, it falls back to the system configuration.
        Attempts to set the system hostname to the retrieved value.

        Returns:
            bool: STATUS_OK if the hostname is successfully set, STATUS_NOK otherwise.
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
    
    def set_hostname_os(self, hostname: str) -> bool:
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
                # with open('/etc/hostname', 'w') as f:
                #    f.write(hostname + '\n')

                # Ensure the change is recognized without a reboot
                self.run(['hostname', hostname])
                
                self.log.debug(f"set_hostname_os() -> Hostname successfully set to {hostname}")

            except Exception as e:
                self.log.error(f"set_hostname_os(): Failed to set hostname: {e}")
                return STATUS_NOK
        
        else:
            self.log.error(f"set_hostname_os(): Setting hostname not supported for OS: {current_os}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_hostname_os(self) -> str:
        """
        Get the current static hostname using the `hostnamectl --static` command.

        Returns:
            str: The current static hostname.
        """
        hostname = os.uname().nodename
        self.log.debug(f'get_hostname() -> {hostname}')
        return hostname
    
    def get_run_log(self) -> List[str]:
        """
        Retrieve the run log from the RunLog utility class.

        Returns:
            List[str]: A list of strings representing each line of the run log file.

        Example:
            >>> instance = SomeOtherClass()
            >>> log_contents = instance.get_run_log()
            >>> for line in log_contents:
            >>>     print(line)
        """
        return RunLog().get_run_log()
    
    