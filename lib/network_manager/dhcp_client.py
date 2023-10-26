from enum import Enum
import logging
import subprocess
from lib.network_manager.common.sysctl import SysCtl
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

    Args:
        None

    Attributes:
        log (logging.Logger): The logger for this class.

    Methods:
        enable_dhcpv4(interface_name: str) -> bool: Enable DHCPv4 on the specified interface.
        enable_dhcpv6(interface_name: str) -> bool: Enable DHCPv6 on the specified interface.
        disable_dhcpv4(interface_name: str) -> bool: Disable DHCPv4 on the specified interface.
        disable_dhcpv6(interface_name: str) -> bool: Disable DHCPv6 on the specified interface.
        restart_dhcp_service() -> bool: Restart the DHCP client service.

    """
    def __init__(self):
        super().__init()
        self.log = logging.getLogger(self.__class__.__name())
        self.log.setLevel(RSLGS().NAT)

    def enable_dhcpv4(self, interface_name: str) -> bool:
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

    def enable_dhcpv6(self, interface_name: str) -> bool:
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

    def disable_dhcpv4(self, interface_name: str) -> bool:
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


    def disable_dhcpv6(self, interface_name: str) -> bool:
        """
        Disable DHCPv6 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to disable DHCPv6 on.

        Returns:
            bool: STATUS_OK if DHCPv6 disabling was successful, STATUS_NOK otherwise.
        """
        command = ["dhclient", "-x", interface_name]
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Unable to disable DHCPv6 client on interface: {interface_name}")
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
            self.log.error("Unable to restart DHCP client service")
            return STATUS_NOK
        
        return STATUS_OK
