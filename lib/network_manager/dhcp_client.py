from enum import Enum
import logging
import shutil
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_manager import NetworkManager

class DHCPVersion(Enum):
    """An enumeration of DHCP versions: DHCPv4 and DHCPv6."""
    DHCP_V4 = 'DHCPv4'
    DHCP_V6 = 'DHCPv6'

class DHCPClient(NetworkManager):
    """
    A class for managing DHCP clients.

    This class provides methods to enable and disable DHCP clients for IPv4 and IPv6 on
    specific network interfaces, as well as restarting the DHCP client service.

    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT)

    def is_dhclient_available(self) -> bool:
        """
        Check if dhclient is available on the system.

        Returns:
            bool: True if dhclient is available, False otherwise.
        """
        return shutil.which("dhclient") is not None

    def set_dhcp_client_interface_service(self, interface_name, dhcp_version: DHCPVersion, enable_dhcp_client=True) -> bool:
        """
        Set the DHCP client service for the specified interface and version.

        Args:
            interface_name (str): The name of the network interface to configure DHCP on.
            dhcp_version (DHCPVersion): The DHCP version (DHCP_V4 or DHCP_V6).
            enable_dhcp_client (bool): If True, enable DHCP; if False, disable DHCP.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if dhcp_version == DHCPVersion.DHCP_V4:
            if enable_dhcp_client:
                result = self._enable_dhcpv4(interface_name)
                if result:
                    self.log.error(f"Failed to enable DHCPv4 client on interface {interface_name}")
                    return STATUS_NOK
            else:
                result = self._disable_dhcpv4(interface_name)
                if result:
                    self.log.error(f"Failed to disable DHCPv4 client on interface {interface_name}")
                    return STATUS_NOK
        
        elif dhcp_version == DHCPVersion.DHCP_V6:
            if enable_dhcp_client:
                result = self._enable_dhcpv6(interface_name)
                if result:
                    self.log.error(f"Failed to enable DHCPv6 client on interface {interface_name}")
                    return STATUS_NOK
            else:
                result = self._disable_dhcpv6(interface_name)
                if result:
                    self.log.error(f"Failed to disable DHCPv6 client on interface {interface_name}")
                    return STATUS_NOK

        return STATUS_OK

    def restart_dhcp_service(self) -> bool:
        """
        Restart the DHCP client service.

        Returns:
            bool: STATUS_OK if the DHCP client service restart was successful, STATUS_NOK otherwise.
        """
        command = ["systemctl", "restart", "dhclient.service"]
        
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Unable to restart DHCP client service - Reason: {result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def _enable_dhcpv4(self, interface_name: str) -> bool:
        """
        Enable DHCPv4 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to enable DHCPv4 on.

        Returns:
            bool: STATUS_OK if DHCPv4 enabling was successful, STATUS_NOK otherwise.
        """
        command = ["dhclient", interface_name]
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Unable to disable DHCPv4 client on interface: {interface_name}")
            return STATUS_NOK
        return STATUS_OK

    def _enable_dhcpv6(self, interface_name: str) -> bool:
        """
        Enable DHCPv6 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to enable DHCPv6 on.

        Returns:
            bool: STATUS_OK if DHCPv6 enabling was successful, STATUS_NOK otherwise.
        """
        command = ["dhclient", "-6", interface_name]
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Unable to disable DHCPv6 client on interface: {interface_name}")
            return STATUS_NOK
        return STATUS_OK

    def _disable_dhcpv4(self, interface_name: str) -> bool:
        """
        Disable DHCPv4 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to disable DHCPv4 on.

        Returns:
            bool: STATUS_OK if DHCPv4 disabling was successful, STATUS_NOK otherwise.
        """
        command = ["dhclient", "-r", interface_name]
        result = self.run(command)
        if result.exit_code:
            self.log.error(f"Unable to disable DHCPv4 client on interface: {interface_name}")
            return STATUS_NOK
        return STATUS_OK

    def _disable_dhcpv6(self, interface_name: str) -> bool:
        """
        Disable DHCPv6 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to disable DHCPv6 on.

        Returns:
            bool: STATUS_OK if DHCPv6 disabling was successful, STATUS_NOK otherwise.
        """
        command = ["dhclient", "-rq", interface_name]
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Unable to disable DHCPv6 client on interface: {interface_name}")
            return STATUS_NOK
        return STATUS_OK
