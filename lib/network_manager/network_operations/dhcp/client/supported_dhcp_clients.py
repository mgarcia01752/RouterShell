from enum import Enum
from ipaddress import ip_address
import ipaddress
import logging
from abc import ABC, abstractmethod
from typing import List

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.inet import InetServiceLayer
from lib.network_manager.common.run_commands import RunCommand
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.system.os.os import OSChecker, SupportedOS

class SupportedDhcpClients(Enum):
    """
    Enumeration of supported DHCP clients.

    Attributes:
        UDHCPC (str): The DHCP (IPv4) client provided by BusyBox, commonly used in lightweight and embedded Linux systems.
        UDHCPC6 (str): The DHCP (IPv6) client provided by BusyBox, commonly used in lightweight and embedded Linux systems.
        DHCPCD (str): The ISC DHCP client with dual stack support (IPv4 and IPv6), suitable for a variety of systems and scenarios.
        DHCLIENT (str): The ISC DHCP client with dual stack support, which was deprecated in 2022. This client is still available but not recommended for new deployments.
    """
    # BusyBox
    UDHCPC = 'udhcpc'
    UDHCPC6 = 'udhcpc6'
    
    # ISC (Dual Stack Support)
    DHCPCD = 'dhcpcd'
    
    # ISC Deprecated 2022 (Dual Stack Support)
    DHCLIENT = 'dhclient'

class SupportedDhcpClientsDHCPVersion(Enum):
    """
    Enumeration of supported DHCP clients with specific versions for IPv4 and IPv6.

    Attributes:
        UDHCPC_V4 (str): The BusyBox DHCP client for IPv4, commonly used in lightweight and embedded Linux systems.
        UDHCPC_V6 (str): The BusyBox DHCP client for IPv6.
        DHCPCD_V4 (str): The ISC DHCP client (dhcpcd) with dual stack support for IPv4, suitable for a variety of systems and scenarios.
        DHCPCD_V6 (str): The ISC DHCP client (dhcpcd) with dual stack support for IPv6.
        DHCLIENT_V4 (str): The ISC DHCP client (dhclient) with dual stack support for IPv4, which was deprecated in 2022. This client is still available but not recommended for new deployments.
        DHCLIENT_V6 (str): The ISC DHCP client (dhclient) with dual stack support for IPv6, which was deprecated in 2022. This client is still available but not recommended for new deployments.
    """
    # BusyBox
    UDHCPC_V4 = 'udhcpc'
    UDHCPC_V6 = 'udhcpc6'
    
    # ISC (Dual Stack Support)
    DHCPCD_V4 = 'dhcpcd'
    DHCPCD_V6 = 'dhcpcd'
    
    # ISC Deprecated 2022 (Dual Stack Support)
    DHCLIENT_V4 = 'dhclient'
    DHCLIENT_V6 = 'dhclient'


class DHCPClientFactory:
    """
    A factory class to get the supported DHCP client based on the interface name and optional override.
    """
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT_FACTORY)      
          
    def get_supported_dhcp_client(self, interface_name: str, auto_sdc_override=None) -> 'DHCPClientOperations':
        """
        Get the supported DHCP client for the specified interface.

        Args:
            interface_name (str): The name of the network interface.
            auto_sdc_override (SupportedDhcpClients, optional): Override for the DHCP client.

        Returns:
            DHCPClientOperations: An instance of the appropriate DHCP client operations class.
        """

        if auto_sdc_override:
            if auto_sdc_override == SupportedDhcpClients.UDHCPC:
                self.log.debug(f'Selecting Dhcp Client: {auto_sdc_override.name}')
                return DHCPClientOperations_udhcpc(interface_name)

            elif auto_sdc_override == SupportedDhcpClients.DHCPCD:
                self.log.debug(f'Selecting Dhcp Client: {auto_sdc_override.name}')
                return DHCPClientOperations_dhcpcd(interface_name)

            elif auto_sdc_override == SupportedDhcpClients.DHCLIENT:
                self.log.debug(f'Selecting Dhcp Client: {auto_sdc_override.name}')
                return DHCPClientOperations_dhclient(interface_name)
        else:
            current_os = OSChecker().get_current_os()
            
            if current_os == SupportedOS.BUSY_BOX:
                self.log.debug(f'Auto Selecting Dhcp Client: {SupportedDhcpClients.UDHCPC.name} on {current_os.name} OS')
                return DHCPClientOperations_udhcpc(interface_name)

            elif current_os == SupportedOS.UBUNTU:
                auto_sdc = self._auto_find_dhcp_client()
                
                if auto_sdc == SupportedDhcpClients.DHCPCD:
                    self.log.debug(f'Auto Selecting Dhcp Client: {auto_sdc.name} on {current_os.name} OS')
                    return DHCPClientOperations_dhcpcd(interface_name)

                elif auto_sdc == SupportedDhcpClients.DHCLIENT:
                    self.log.debug(f'Auto Selecting Dhcp Client: {auto_sdc.name} on {current_os.name} OS')
                    return DHCPClientOperations_dhclient(interface_name)
                
        # If no supported DHCP client is found, raise an exception or handle it appropriately
        raise DHCPClientException(f"No supported DHCP client found for interface: {interface_name}")
    
    def _auto_find_dhcp_client(self) -> SupportedDhcpClients:
        """
        Automatically find a supported DHCP client.

        Returns:
            SupportedDhcpClients: The DHCP client found.
        """
        # Maintain this order BusyBox -> General Linux Distro
        if self._check_command_exists("udhcpc"):
            return SupportedDhcpClients.UDHCPC
        
        elif self._check_command_exists("dhcpcd"):
            return SupportedDhcpClients.DHCPCD
        
        elif self._check_command_exists("dhclient"):
            return SupportedDhcpClients.DHCLIENT
        
        else:
            raise DHCPClientException("No supported DHCP client found.")
    
    def _check_command_exists(self, command: str) -> bool:
        """
        Check if a command exists in the system.

        Args:
            command (str): The command to check.

        Returns:
            bool: True if the command exists, False otherwise.
        """
        import shutil
        return shutil.which(command) is not None
            
class DHCPClientException(Exception):
    """
    Custom exception class for DHCP client operations.

    Attributes:
        message (str): The error message.
        command (str): The command that caused the exception (if applicable).
    """

    def __init__(self, message: str, command: str = None):
        self.message = message
        self.command = command
        super().__init__(self.message)

    def __str__(self):
        if self.command:
            return f"{self.message} | Command: {self.command}"
        return self.message                    

class DHCPClientOperations(ABC, RunCommand):
    """
    Abstract base class for DHCP client operations on a network interface.
    
    This class provides a template for implementing various DHCP client operations
    such as checking client availability, configuring network settings, and managing
    the DHCP client lifecycle.

    Attributes:
        _interface_name (str): The name of the network interface.

    Methods:
        is_client_available(): Check if the DHCP client is available.
        get_interface(): Get the name of the network interface.
        remove_interface(): Remove the network interface configuration.
        set_inet4(): Configure the interface with IPv4 settings.
        set_inet6(): Configure the interface with IPv6 settings.
        set_dual_stack(): Configure the interface with both IPv4 and IPv6 settings.
        start(): Start the DHCP client.
        stop(): Stop the DHCP client.
        restart(): Restart the DHCP client.
        get_inet(): Retrieve the current IP address assigned to the interface.
        release_inet(): Release the current IP address.
        renew_inet(): Renew the IP address for the interface.
    """

    def __init__(self, interface_name: str, sdc: SupportedDhcpClients):
        super().__init__()
        RunCommand().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SUPPORTED_CLIENTS_ABC)
        self._interface_name = interface_name
        self._sdc = sdc
        
        if not self.is_client_available():
            raise DHCPClientException(f"DHCP client is not available.", self._sdc.value)        

    def is_client_available(self) -> bool:
        """
        Check if the udhcpc DHCP client is available on the system.

        Returns:
            bool: True if udhcpc is available, False otherwise.
        """
        import shutil
        return shutil.which(self._sdc.value) is not None

    def get_interface(self) -> str:
        """
        Get the name of the network interface.

        Returns:
            str: The name of the network interface.
        """
        return self._interface_name

    @abstractmethod
    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    def set_dual_stack(self) -> bool:
        """
        Configure the interface with both IPv4 and IPv6 settings.
        
        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        inet4_status = self.set_inet4()
        inet6_status = self.set_inet6()
        
        if inet4_status == STATUS_OK and inet6_status == STATUS_OK:
            return STATUS_OK
        else:
            self.log.error(f'Unable to set dual stack on interface: {self.get_interface()}')
            return STATUS_NOK

    @abstractmethod
    def start(self) -> bool:
        """
        Start the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def restart(self) -> bool:
        """
        Restart the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    def get_inet(self) -> List[ip_address]:
        """
        Retrieve all IP addresses assigned to the interface, including both IPv4 and IPv6 addresses.

        Returns:
            List[ipaddress.ip_address]: A list of IP addresses assigned to the interface. This list can include both IPv4 and IPv6 addresses.
            
        """
        return InetServiceLayer().get_interface_ip_addresses(self.get_interface())

    @abstractmethod
    def release_inet(self) -> bool:
        """
        Release the current IP address.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def renew_inet(self) -> ipaddress:
        """
        Renew the IP address for the interface.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        pass

class DHCPClientOperations_udhcpc(DHCPClientOperations):
    def __init__(self, interface_name: str):
        """
        Initialize the DHCPClient_udhcpc with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name,SupportedDhcpClients.UDHCPC)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT_UDHCPC)

        self._dco_udhcpc6 = DHCPClientOperations_udhcpc6(interface_name)
        
    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        #Busy Box pkill implementation
        result = self.run(['pkill', f'udhcpc -i {self._interface_name}'])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['udhcpc', '-i', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings. Note: udhcpc does not support IPv6 natively.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._dco_udhcpc6.set_inet6()

    def start(self) -> bool:
        """
        Start the DHCP client (udhcpc) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.set_inet4()

    def stop(self) -> bool:
        """
        Stop the DHCP client (udhcpc) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.remove_interface()

    def restart(self) -> bool:
        """
        Restart the DHCP client (udhcpc) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        stop_status = self.stop()
        start_status = self.start()
        return STATUS_OK if stop_status == STATUS_OK and start_status == STATUS_OK else STATUS_NOK

    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ipaddress.ip_address:
        """
        Renew the IP address for the interface by restarting udhcpc.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

class DHCPClientOperations_udhcpc6(DHCPClientOperations):
    def __init__(self, interface_name: str):
        """
        Initialize the DHCPClient_udhcpc6 with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name,SupportedDhcpClients.UDHCPC)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT_UDHCPC6)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['pkill', f'udhcpc6 -i {self._interface_name}'])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings. Note: udhcpc6 does not support IPv4.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self.log.error('udhcpc6 does not support IPv4.')
        return STATUS_NOK

    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['udhcpc6', '-i', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def start(self) -> bool:
        """
        Start the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.set_inet6()

    def stop(self) -> bool:
        """
        Stop the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.remove_interface()

    def restart(self) -> bool:
        """
        Restart the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        stop_status = self.stop()
        start_status = self.start()
        return STATUS_OK if stop_status == STATUS_OK and start_status == STATUS_OK else STATUS_NOK

    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ipaddress.ip_address:
        """
        Renew the IP address for the interface by restarting udhcpc6.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

class DHCPClientOperations_dhcpcd(DHCPClientOperations):
    def __init__(self, interface_name: str):
        """
        Initialize the DHCPClient_dhcpcd with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name,SupportedDhcpClients.DHCPCD)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT_DHCPCD)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhcpcd', '--release', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhcpcd', '-4', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhcpcd', '-6', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def start(self) -> bool:
        """
        Start the DHCP client (dhcpcd) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhcpcd', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def stop(self) -> bool:
        """
        Stop the DHCP client (dhcpcd) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhcpcd', '--release', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def restart(self) -> bool:
        """
        Restart the DHCP client (dhcpcd) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        stop_status = self.stop()
        start_status = self.start()
        return STATUS_OK if stop_status == STATUS_OK and start_status == STATUS_OK else STATUS_NOK

    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ip_address:
        """
        Renew the IP address for the interface by restarting dhcpcd.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

class DHCPClientOperations_dhclient(DHCPClientOperations):
    def __init__(self, interface_name: str):
        """
        Initialize the DHCPClient_dhclient with a network interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name,SupportedDhcpClients.DHCLIENT)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_CLIENT_DHCLIENT)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhclient', '-r', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhclient', '-4', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhclient', '-6', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def start(self) -> bool:
        """
        Start the DHCP client (dhclient) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhclient', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def stop(self) -> bool:
        """
        Stop the DHCP client (dhclient) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        result = self.run(['dhclient', '-r', self._interface_name])
        return STATUS_OK if result.exit_code == 0 else STATUS_NOK

    def restart(self) -> bool:
        """
        Restart the DHCP client (dhclient) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        stop_status = self.stop()
        start_status = self.start()
        return STATUS_OK if stop_status == STATUS_OK and start_status == STATUS_OK else STATUS_NOK

    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ip_address:
        """
        Renew the IP address for the interface by restarting dhclient.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

    