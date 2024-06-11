import logging
import textwrap
from typing import Dict, Tuple

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_NOK, STATUS_OK, Status
class SystemDatabase:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().SYSTEM_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()
    
    def set_hostname(cls, host_name: str) -> bool:
        """
        Sets the hostname in the system database.

        Updates the hostname in the database with the provided hostname.

        Args:
            host_name (str): The new hostname to set.

        Returns:
            bool: True if the hostname is successfully updated, False otherwise.
        """
        return cls.rsdb.update_hostname(host_name).status
    
    def get_hostname_db(cls) -> str:
        """
        Retrieves the hostname from the system database.

        Fetches the current hostname from the database.

        Returns:
            str: The current hostname, else None.
        """
        result = cls.rsdb.select_hostname()
        if result.status == STATUS_OK and result.result:
            return result.result.get('Hostname')
        return None

    
    def set_banner_motd(cls, motd_banner:str) -> bool:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            cls: The RouterShellDB class.
            motd_banner (str): The new banner text.

        Returns:
            bool: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """        
        return cls.rsdb.update_banner_motd(motd_banner).status
    
    def get_banner_motd(cls) -> Tuple[bool, str]:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration.

        Args:
            cls: The RouterShellDB class

        Returns:
            Tuple[bool, str]: A tuple containing the status (STATUS_OK | STATUS_NOK) of the operation and the formatted banner text with lines
        """
        result = cls.rsdb.select_banner_motd()

        return result.status, result.result.get('BannerMotd')

    def get_telnet_server_status(cls) -> bool:
        """
        Get the status of the Telnet server.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.select_global_telnet_server().status

    def set_telnet_server_status(cls, telnet_server_status: Status) -> bool:
        """
        Set the status of the Telnet server.

        Args:
            telnet_server_status (Status): The desired status of the Telnet server (ENABLE or DISABLE).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        tss = telnet_server_status == Status.ENABLE
        return cls.rsdb.insert_global_telnet_server(tss).status

    def get_ssh_server_status(cls) -> bool:
        """
        Get the status of the SSH server.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.select_global_ssh_server().status

    def set_ssh_server_status(cls, ssh_server_status: Status) -> bool:
        """
        Set the status of the SSH server.

        Args:
            ssh_server_status (Status): The desired status of the SSH server (ENABLE or DISABLE).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        tss = ssh_server_status == Status.ENABLE
        return cls.rsdb.insert_global_ssh_server(tss).status
              