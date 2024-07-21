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
    
    def set_hostname_db(cls, host_name: str) -> bool:
        """
        Sets the hostname in the system database.

        Updates the hostname in the database with the provided hostname.

        Args:
            host_name (str): The new hostname to set.

        Returns:
            bool: STATUS_OK if the hostname is successfully updated, STATUS_NOK otherwise.
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

    def get_telnet_server_status(cls) -> Tuple[bool, Dict]:
        """
        Retrieve the Telnet server status and port from the database.

        Returns:
            Tuple[bool, Dict]: A tuple containing a boolean indicating the success of the operation and a dictionary.
                            The dictionary contains the Telnet server status ('Enable') and port ('Port') if the 
                            operation is successful. If the operation fails, the boolean is STATUS_NOK and the dictionary is empty.
        """
        try:
            result = cls.rsdb.select_global_telnet_server()
            if result.status:
                cls.log.error(f"Failed to retrieve Telnet server status: {result.reason}")
                return STATUS_NOK, {}
            
            return STATUS_OK, result.result
        
        except Exception as e:
            cls.log.error(f"Unexpected error while retrieving Telnet server status: {e}")
            return STATUS_NOK, {}

    def set_telnet_server_status(cls, telnet_server_status: bool, port: int) -> bool:
        """
        Sets the status of the Telnet server and updates the port configuration.

        Parameters:
        telnet_server_status (bool): The desired status of the Telnet server (True to enable, False to disable).
        port (int): The port number for the Telnet server.

        Returns:
        bool: The status indicating whether the update was successful.
        """
        result = cls.rsdb.update_global_telnet_server(telnet_server_status, port)
        return result.status

    def get_ssh_server_status(cls) -> Tuple[bool, Dict]:
        """
        Retrieve the SSH server status and port from the database.

        Returns:
            Tuple[bool, Dict]: A tuple containing a boolean indicating the success of the operation 
                               and a dictionary. The dictionary contains the SSH server status ('Enable') 
                               and port ('Port') if the operation is successful. If the operation fails, 
                               the boolean is STATUS_NOK and the dictionary is empty.
        """
        try:
            result = cls.rsdb.select_global_ssh_server()
            if result.status:
                cls.log.error(f"Failed to retrieve SSH server status: {result.reason}")
                return STATUS_NOK, {}
            
            return STATUS_OK, result.result
        
        except Exception as e:
            cls.log.error(f"Unexpected error while retrieving SSH server status: {e}")
            return STATUS_NOK, {}

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
              