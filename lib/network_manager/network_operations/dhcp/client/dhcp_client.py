import logging
from typing import List

from lib.common.constants import STATUS_NOK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.db.dhcp_client_db import DHCPClientDatabase
from lib.network_manager.network_operations.dhcp.client.supported_dhcp_clients import DHCPClientFactory, DHCPClientOperations
from lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion, DHCPStatus

class DHCPClientException(Exception):
    """
    Custom exception for DHCP client operations.

    Attributes:
        message (str): Error message for the exception.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"DHCPClientException: {self.message}"

class DHCPClient:
    """
    A class for managing DHCP client operations on a network interface.

    This class provides methods to start, stop, and restart DHCP clients for IPv4,
    IPv6, or dual stack configurations on a specific network interface. It also retrieves
    DHCP client flow logs.

    Attributes:
        _interface_name (str): The name of the network interface.
        _dhcp_stack_version (DHCPStackVersion): The DHCP stack version to use.
        _dhcp_client (DHCPClientOperations): The specific DHCP client instance for the network interface.
        _last_status (DHCPClientStatus): The last status of the DHCP client.

    Methods:
        start(): Start the DHCP client with the configured stack version.
        stop(): Stop the DHCP client.
        restart(): Restart the DHCP client service.
        get_flow_log(): Retrieve DHCP client flow logs from the system journal.
        get_last_status(): Get the last status of the DHCP client.
    """
    def __init__(self, interface_name: str, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient with the network interface name and DHCP stack version.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_stack_version (DHCPStackVersion): The DHCP stack version to use.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT)
        
        self._interface_name = interface_name
        self._dhcp_stack_version = dhcp_stack_version
        
        self._dhcp_client : DHCPClientOperations = DHCPClientFactory().get_supported_dhcp_client(interface_name, dhcp_stack_version)
    
    def get_last_status(self) -> DHCPStatus:
        """
        Get the last status of the DHCP client.

        Returns:
            DHCPClientStatus: The last status of the DHCP client.
        """
        return self._dhcp_client.get_last_status()
                
    def start(self) -> bool:
        """
        Start the DHCP client with the configured stack version.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        self.log.debug(f'Start DHCP client on interface {self._dhcp_client.get_interface()}')
        if self._dhcp_client.start():
            return STATUS_NOK
        
        return DHCPClientDatabase().update_db_dhcp_client(self._dhcp_client.get_interface(), self._dhcp_stack_version.value)
        
    def stop(self) -> bool:
        """
        Stop the DHCP client.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        self.log.debug(f'Stop DHCP client on interface {self._dhcp_client.get_interface()}')
        if self._dhcp_client.stop():
            return STATUS_NOK
        
        return DHCPClientDatabase().remove_db_dhcp_client(self._dhcp_client.get_interface(), self._dhcp_stack_version.value)
    
    def restart(self) -> bool:
        """
        Restart the DHCP client service.

        Returns:
            bool: STATUS_OK if the DHCP client service restart was successful, STATUS_NOK otherwise.
        """        
        return self._dhcp_client.restart()

    def get_flow_log(self) -> List[str]:
        """
        Retrieve DHCP client flow logs (DORA/SAAR) from the system journal.

        Returns:
            List[str]: A list of DHCP client flow log entries.
        """
        # Implement log retrieval from the system journal if necessary
        return []
