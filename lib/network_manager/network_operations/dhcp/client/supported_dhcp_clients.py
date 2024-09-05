import ipaddress
import logging
import shutil

from enum import Enum
from typing import List
from abc import ABC, abstractmethod
from ipaddress import ip_address

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.inet import InetServiceLayer
from lib.network_manager.common.run_commands import RunCommand, RunResult
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion, DHCPStatus
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
    # BusyBox (Need both to Support Dual-Stack)
    UDHCPC = 'udhcpc'
    UDHCPC6 = 'udhcpc6'
    
    # ISC (Dual-Stack Support)
    DHCPCD = 'dhcpcd'
    
    # ISC Deprecated 2022 (Dual-Stack Support)
    DHCLIENT = 'dhclient'

class SupportedDhcpClientsDHCPVersion(Enum):
    """
    Enumeration of supported DHCP clients with specific versions for IPv4 and IPv6.

    Attributes:
        UDHCPC_V4 (str): The BusyBox DHCP client for IPv4, commonly used in lightweight and embedded Linux systems.
        UDHCPC_V6 (str): The BusyBox DHCP client for IPv6.
        DHCPCD_V4 (str): The ISC DHCP client (dhcpcd) with dual stack support for IPv4, suitable for a variety of systems and scenarios.
        DHCPCD_V6 (str): The ISC DHCP client (dhcpcd) with dual stack support for IPv6.
        DHCLIENT_V4 (str): The ISC DHCP client (dhclient) with dual stack support for IPv4, which was deprecated in 2022. 
                           This client is still available but not recommended for new deployments.
        DHCLIENT_V6 (str): The ISC DHCP client (dhclient) with dual stack support for IPv6, which was deprecated in 2022. 
                           This client is still available but not recommended for new deployments.
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
    
    _DHCPClientOperationsList:List['DHCPClientOperations'] = []
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_FACTORY)      
          
    def get_supported_dhcp_client(
        self, interface_name: str, dhcp_stack_version: DHCPStackVersion, auto_sdc_override=None
    ) -> 'DHCPClientOperations':
        """
        Determines and returns the appropriate DHCP client operations object based on 
        the specified interface name, DHCP stack version, and optional override.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_stack_version (DHCPStackVersion): The version of the DHCP stack to use.
            auto_sdc_override (Optional[SupportedDhcpClients]): Optional override for 
                selecting the DHCP client. If provided, it determines which DHCP client 
                will be used regardless of the current OS. If not provided, the selection 
                is based on the current OS.

        Returns:
            DHCPClientOperations: An instance of the appropriate DHCP client operations 
                class based on the provided arguments and conditions.
        """
        # Track DHCPClientOperations
        dco: DHCPClientOperations = None
        
        if auto_sdc_override:

            self.log.debug(f'Selecting DHCP Client: {auto_sdc_override.name}')
            if auto_sdc_override == SupportedDhcpClients.UDHCPC:
                dco = DHCPClientOperations_udhcpc(interface_name, dhcp_stack_version)

            elif auto_sdc_override == SupportedDhcpClients.DHCPCD:
                dco = DHCPClientOperations_dhcpcd(interface_name, dhcp_stack_version)

            elif auto_sdc_override == SupportedDhcpClients.DHCLIENT:
                dco = DHCPClientOperations_dhclient(interface_name, dhcp_stack_version)

        else:
            current_os = OSChecker().get_current_os()
            self.log.debug(f'Auto Selecting DHCP Client on {current_os.name} OS')
            
            if current_os == SupportedOS.BUSY_BOX:
                dco = DHCPClientOperations_udhcpc(interface_name, dhcp_stack_version)

            elif current_os == SupportedOS.UBUNTU:
                auto_sdc = self._auto_find_dhcp_client()

                if auto_sdc == SupportedDhcpClients.DHCPCD:
                    dco = DHCPClientOperations_dhcpcd(interface_name, dhcp_stack_version)

                elif auto_sdc == SupportedDhcpClients.DHCLIENT:
                    dco = DHCPClientOperations_dhclient(interface_name, dhcp_stack_version)

            else:
                raise NotImplementedError(f'Unsupported OS: {current_os.name}')
            
        if not dco:
            raise Exception(f'Failed to determine DHCP Client Operations object for {interface_name}')
        
        DHCPClientFactory._DHCPClientOperationsList.append(dco)
        return dco

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
        Implemented Methods:
            get_interface(): Get the name of the network interface.
            set_dual_stack(): Configure the interface with both IPv4 and IPv6 settings.
            get_inet(): Retrieve the current IP address assigned to the interface.
            is_client_available(): Check if the DHCP client is available.
            get_dhcp_client(): Retrieve the supported DHCP client.
            start(): Start the DHCP client.
            restart(): Restart the DHCP client.
            set_auto(): Start the DHCP client based

        Abstract Methods:
            remove_interface(): Remove the network interface configuration.
            set_inet4(): Configure the interface with IPv4 settings.
            set_inet6(): Configure the interface with IPv6 settings.
            stop(): Stop the DHCP client.
            release_inet(): Release the current IP address.
            renew_inet(): Renew the IP address for the interface.
    """

    def __init__(self, interface_name: str, dhcp_stack_version: DHCPStackVersion, sdc: SupportedDhcpClients):
        super().__init__()
        RunCommand().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SUPPORTED_CLIENTS_ABC)
        self._interface_name = interface_name
        self._dsv = dhcp_stack_version
        self._sdc = sdc
        self._last_dhcp_client_status = DHCPStatus.STOP
        
        if not self.is_client_available():
            raise DHCPClientException(f"DHCP client is not available.", self._sdc.value)
    
    def get_dhcp_stack_version(self) -> DHCPStackVersion:
        """
        Get the DHCP stack version being used.

        Returns:
            DHCPStackVersion: The DHCP stack version.
        """
        return self._dsv

    def get_dhcp_client(self) -> SupportedDhcpClients:
        """
        Retrieve the supported DHCP client.

        Returns:
            SupportedDhcpClients: The supported DHCP client.
        """
        return self._sdc    

    def is_client_available(self) -> bool:
        """
        Check if the udhcpc DHCP client is available on the system.

        Returns:
            bool: True if udhcpc is available, False otherwise.
        """
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
        
    def set_auto(self) -> bool:
        """
        Automatically configure the interface with the appropriate DHCP settings based on the stack version.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.get_dhcp_stack_version() == DHCPStackVersion.DHCP_V4:
            return self.set_inet4()
        elif self.get_dhcp_stack_version() == DHCPStackVersion.DHCP_V6:
            return self.set_inet6()
        elif self.get_dhcp_stack_version() == DHCPStackVersion.DHCP_DUAL_STACK:
            return self.set_dual_stack()
        else:
            self.log.error(f'Unable to set auto on interface: {self.get_interface()}')
            return STATUS_NOK

    def start(self) -> bool:
        """
        Start the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.START
        return self.set_auto()

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return STATUS_OK

    def restart(self) -> bool:
        """
        Restart the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        stop_status = self.stop()
        start_status = self.start()
        self._last_dhcp_client_status = DHCPStatus.RESTART
        return STATUS_OK if stop_status == STATUS_OK and start_status == STATUS_OK else STATUS_NOK

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
    
    def get_last_status(self) -> DHCPStatus:
        """
        Get the last status of the DHCP client.
        """
        return self._last_dhcp_client_status

    def _execute_command(self, command: List[str]) -> bool:
        """
        Executes a shell command and logs the result.

        Args:
            command (List[str]): The command to be executed as a list of strings.

        Returns:
            bool: STATUS_OK if the command executed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"Executing command: {command}")
        result : RunResult = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Command failed with error: {result.stderr}")
            return STATUS_NOK
        
        self.log.debug(f"Command executed successfully: {result.stdout}")
        return STATUS_OK

class DHCPClientOperations_udhcpc(DHCPClientOperations):
    def __init__(self, interface_name: str, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_udhcpc with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.UDHCPC)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_UDHCPC)

        self._dco_udhcpc6 = DHCPClientOperations_udhcpc6(interface_name, DHCPStackVersion.DHCP_V6)
        
    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        #Busy Box pkill implementation
        return self._execute_command(['pkill', f'udhcpc -i {self._interface_name}'])
        
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['udhcpc', '-i', self._interface_name])
    
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings. Note: udhcpc does not support IPv6 natively.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._dco_udhcpc6.set_inet6()

    def stop(self) -> bool:
        """
        Stop the DHCP client (udhcpc) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._get_last_status = DHCPStatus.STOP
        return self.remove_interface()

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
    def __init__(self, interface_name: str, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_udhcpc6 with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.UDHCPC)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_UDHCPC6)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['pkill', f'udhcpc6 -i {self._interface_name}'])
    
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
        return self._execute_command(['udhcpc6', '-i', self._interface_name])
    
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
        self._last_dhcp_client_status = DHCPStatus.STOP
        return self.remove_interface()

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
    def __init__(self, interface_name: str, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_dhcpcd with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.DHCPCD)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_DHCPCD)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhcpcd', '--release', self._interface_name])
    
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhcpcd', '-4', self._interface_name])
    
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhcpcd', '-6', self._interface_name])
    
    def stop(self) -> bool:
        """
        Stop the DHCP client (dhcpcd) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return self._execute_command(['dhcpcd', '--release', self._interface_name])
        
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
    def __init__(self, interface_name: str, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_dhclient with a network interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.DHCLIENT)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_DHCLIENT)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhclient', '-r', self._interface_name])
        
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhclient', '-4', self._interface_name])
        
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhclient', '-6', self._interface_name])
        
    def stop(self) -> bool:
        """
        Stop the DHCP client (dhclient) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return self._execute_command(['dhclient', '-r', self._interface_name])
        
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

    