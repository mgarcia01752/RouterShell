from enum import Enum
import logging
import shutil
from typing import List

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.run_commands import RunCommand

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

class DHCPClient(RunCommand):
    """
    A class for managing DHCP clients.

    This class provides methods to enable and disable DHCP clients for IPv4 and IPv6 on
    specific network interfaces, as well as restarting the DHCP client service.
    """
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT)
        
        # Check DHCP client availability during initialization
        if not self.is_dhcp_client_available():
            raise EnvironmentError("No supported DHCP client (udhcpc or dhclient) is installed.")

    def is_dhcp_client_available(self) -> bool:
        """
        Check if either udhcpc or dhclient is available on the system.

        Returns:
            bool: True if either udhcpc or dhclient is available, False otherwise.
        """
        try:
            return shutil.which("udhcpc") is not None or shutil.which("dhclient") is not None
        except Exception as e:
            self.log.error(f"Error checking DHCP client availability: {e}")
            return False

    def set_dhcp_client_interface_service(self, interface_name, dhcp_stack_version: DHCPStackVersion, enable_dhcp_client=True) -> bool:
        """
        Set the DHCP client service for the specified interface and version.

        Args:
            interface_name (str): The name of the network interface to configure DHCP on.
            dhcp_stack_version (DHCPStackVersion): The DHCP version (DHCP_V4 or DHCP_V6 or DHCP_DUAL_STACK).
            enable_dhcp_client (bool): If True, enable DHCP; if False, disable DHCP.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if dhcp_stack_version == DHCPStackVersion.DHCP_V4:
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
        
        elif dhcp_stack_version == DHCPStackVersion.DHCP_V6:
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
        
        elif dhcp_stack_version == DHCPStackVersion.DHCP_DUAL_STACK:

            if enable_dhcp_client:
                result = self._enable_dhcp_dual_stack(interface_name)
                if result:
                    self.log.error(f"Failed to enable DHCPv6 client on interface {interface_name}")
                    return STATUS_NOK
            else:
                result = self._disable_dual_stack(interface_name)
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

    def get_flow_log(self) -> List[str]:
        """
        Retrieve DHCP client flow logs (DORA/SAAR) from the system journal.

        Returns:
            List[str]: A list of DHCP client flow log entries.
        """
        try:
            result = self.run(['journalctl | grep dhclient'], shell=True, sudo=False)

            if result.exit_code:
                return []

            log_entries = result.stdout.split('\n')

            return log_entries

        except Exception as e:
            self.log.error(f"Error retrieving DHCP client flow logs: {e}")
            return []
    
    def _enable_dhcp_dual_stack(self, interface_name:str) -> bool:
        """
        Enable DHCPv4 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to enable DHCPv4 on.

        Returns:
            bool: STATUS_OK if DHCPv4 enabling was successful, STATUS_NOK otherwise.
        """
        try:
            command = self._start_installed_dhcp_client_cmd(interface_name)
        except DHCPClientException as e:
            self.log.error(f"Unable to enable DHCP-DUAL-STACK on interface {interface_name} - Reason: {e}")
            return STATUS_NOK

        result = self.run(command)

        if result.exit_code != 0:
            self.log.error(f"Unable to enable DHCP-DUAL-STACK client on interface: {interface_name} - Reason: {result.stderr}")
            return STATUS_NOK

        self.log.info(f"Successfully enabled DHCP-DUAL-STACK client on interface: {interface_name}")
        return STATUS_OK

    def _disable_dual_stack(self, interface_name:str) -> bool:
        """
        Disable DHCP dual-stack (both DHCPv4 and DHCPv6) on the specified interface.

        Args:
            interface_name (str): The name of the network interface to disable DHCP dual-stack on.

        Returns:
            bool: STATUS_OK if DHCP dual-stack disabling was successful, STATUS_NOK otherwise.
        """
        try:
            command = self._stop_installed_dhcp_client_cmd(interface_name)
            
        except DHCPClientException as e:
            self.log.error(f"Unable to disable DHCP-DUAL-STACK on interface {interface_name} - Reason: {e}")
            return STATUS_NOK

        result = self.run(command)

        if result.exit_code != 0:
            self.log.error(f"Unable to disable DHCP-DUAL-STACK client on interface: {interface_name} - Reason: {result.stderr}")
            return STATUS_NOK

        self.log.info(f"Successfully disabled DHCP-DUAL-STACK client on interface: {interface_name}")
        return STATUS_OK

    def _enable_dhcpv4(self, interface_name: str) -> bool:
        """
        Enable DHCPv4 on the specified interface.

        Args:
            interface_name (str): The name of the network interface to enable DHCPv4 on.

        Returns:
            bool: STATUS_OK if DHCPv4 enabling was successful, STATUS_NOK otherwise.
        """
        try:
            command = self._start_installed_dhcp_client_cmd(interface_name)
        except DHCPClientException as e:
            self.log.error(f"Unable to enable DHCPv4 on interface {interface_name} - Reason: {e}")
            return STATUS_NOK

        result = self.run(command)

        if result.exit_code != 0:
            self.log.error(f"Unable to enable DHCPv4 client on interface: {interface_name} - Reason: {result.stderr}")
            return STATUS_NOK

        self.log.info(f"Successfully enabled DHCPv4 client on interface: {interface_name}")
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
        try:
            command = self._stop_installed_dhcp_client_cmd(interface_name)
        except DHCPClientException as e:
            self.log.error(f"Unable to disable DHCPv4 on interface {interface_name} - Reason: {e}")
            return STATUS_NOK

        result = self.run(command)

        if result.exit_code != 0:
            self.log.error(f"Unable to disable DHCPv4 client on interface: {interface_name} - Reason: {result.stderr}")
            return STATUS_NOK

        self.log.info(f"Successfully disabled DHCPv4 client on interface: {interface_name}")
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

    def _start_installed_dhcp_client_cmd(self, interface_name: str) -> str:
        """
        Generate the appropriate command to use the installed DHCP client (udhcpc or dhclient)
        for a given network interface.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            str: The command to use the installed DHCP client.
        """
        
        if not self.is_dhcp_client_available():
            raise EnvironmentError("No supported DHCP client (udhcpc or dhclient) is installed.")

        if shutil.which("udhcpc"):
            cmd = f"udhcpc -i {interface_name}"
        elif shutil.which("dhclient"):
            cmd = f"dhclient {interface_name}"
        else:
            raise EnvironmentError("No supported DHCP client (udhcpc or dhclient) is installed.")

        return cmd

    def _stop_installed_dhcp_client_cmd(self, interface_name: str) -> str:
        """
        Generate the appropriate command to stop the installed DHCP client (udhcpc or dhclient)
        for a given network interface.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            str: The command to stop the installed DHCP client.
        """
        
        if not self.is_dhcp_client_available():
            raise EnvironmentError("No supported DHCP client (udhcpc or dhclient) is installed.")

        if shutil.which("udhcpc"):
            cmd = f"pkill -f 'udhcpc -i {interface_name}'"
        elif shutil.which("dhclient"):
            cmd = f"dhclient -r {interface_name}"
        else:
            raise EnvironmentError("No supported DHCP client (udhcpc or dhclient) is installed.")

        return cmd