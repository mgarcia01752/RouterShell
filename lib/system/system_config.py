import logging
import textwrap

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK, Common
from lib.db.sqlite_db.router_shell_db import RouterShellDB
from lib.db.system_db import SystemDatabase
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
    
    def set_hostname(self, hostname: str) -> bool:
        """
        Set the system hostname using the `hostnamectl set-hostname` command.

        Args:
            hostname (str): The new hostname to set.

        Returns:
            bool: STATUS_OK if the hostname is set successfully, STATUS_NOK otherwise.
        """
        
        if not Common.is_valid_hostname(hostname):
            self.log.debug(f'Invalid hostname format: {hostname}')
            return STATUS_NOK        
        
        result = self.run(['hostnamectl', 'set-hostname', hostname])
        if result.exit_code:
            self.log.error(f'Unable to set hostname: {hostname}. Reason: {result.stderr}')
            return STATUS_NOK
        
        result = RouterShellDB().update_hostname(hostname)
        
        if result.status:
            self.log.error(f"Unable to add hostname to Router DB, reason: {result.reason}")
            return STATUS_NOK

        return STATUS_OK
    
    def get_hostname(self) -> str:
        """
        Get the current static hostname using the `hostnamectl --static` command.

        Returns:
            str: The current static hostname.
        """
        result = self.run(['hostnamectl', '--static'])
        
        if result.exit_code:
            raise Exception('Failed to retrieve hostname from hostnamectl --static')
        
        return result.stdout.strip()
    