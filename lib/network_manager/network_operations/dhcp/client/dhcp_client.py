from enum import Enum
import logging
from typing import List

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_operations.dhcp.client.supported_dhcp_clients import DHCPClientFactory, DHCPClientOperations

class DHCPStackVersion(Enum):
    """An enumeration of DHCP versions: DHCPv4, DHCPv6, DUAL_STACK"""
    DHCP_V4 = 'DHCPv4'
    DHCP_V6 = 'DHCPv6'
    DHCP_DUAL_STACK = 'DHCPv4v6'

class DHCPClientException(Exception):
    """
    Custom exception for DHCP client operations.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"DHCPClientException: {self.message}"

class DHCPClient:
    """
    A class for managing DHCP clients.

    This class provides methods to enable and disable DHCP clients for IPv4 and IPv6 on
    specific network interfaces, as well as restarting the DHCP client service.
    """
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT)
        
        if not self.is_dhcp_client_available():
            raise EnvironmentError("No supported DHCP client (udhcpc or dhclient) is installed.")

    def is_dhcp_client_available(self) -> bool:
            return True

    def set_dhcp_client_interface_service(self, interface_name:str, 
                                          dhcp_stack_version: DHCPStackVersion, 
                                          enable_dhcp_client: bool=True) -> bool:
        """
        Set the DHCP client service for the specified interface and version.

        Args:
            interface_name (str): The name of the network interface to configure DHCP on.
            dhcp_stack_version (DHCPStackVersion): The DHCP version (DHCP_V4 or DHCP_V6 or DHCP_DUAL_STACK).
            enable_dhcp_client (bool): If True, enable DHCP; if False, disable DHCP.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    def restart_dhcp_service(self) -> bool:
        """
        Restart the DHCP client service.

        Returns:
            bool: STATUS_OK if the DHCP client service restart was successful, STATUS_NOK otherwise.
        """        
        return STATUS_OK

    def get_flow_log(self) -> List[str]:
        """
        Retrieve DHCP client flow logs (DORA/SAAR) from the system journal.

        Returns:
            List[str]: A list of DHCP client flow log entries.
        """
        return []

    def _get_supported_dhcp_client(self) -> DHCPClientOperations:
        return DHCPClientFactory