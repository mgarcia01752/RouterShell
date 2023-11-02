from enum import Enum
import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.dhcp_server_db import DHCPServerDatabase
from lib.network_manager.network_manager import NetworkManager
from lib.network_services.dhcp.common.dhcp_common import DHCPOptionLookup
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSMasqConfigurator
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS


class DNSMasqExitCode(Enum):
    """
    Enum class representing DNSMasq exit codes.

    EXIT CODES:
    0 - Dnsmasq successfully forked into the background, or terminated normally if back-ground is not enabled.
    1 - A problem with configuration was detected.
    2 - A problem with network access occurred (address in use, attempt to use privileged ports without permission).
    3 - A problem occurred with a filesystem operation (missing file/directory, permissions).
    4 - Memory allocation failure.
    5 - Other miscellaneous problem.
    11 or greater - a non-zero return code was received from the lease-script process "init" call or a --conf-script file.
                    The exit code from dnsmasq is the script's exit code with 10 added.
    """

    SUCCESS = 0
    CONFIG_PROBLEM = 1
    NETWORK_ACCESS_PROBLEM = 2
    FILESYSTEM_OPERATION_PROBLEM = 3
    MEMORY_ALLOCATION_FAILURE = 4
    MISC_PROBLEM = 5

    @classmethod
    def from_script_exit_code(cls, script_exit_code):
        """
        Map a script exit code to a DNSMasq exit code.

        Args:
            script_exit_code (int): The script's exit code.

        Returns:
            DNSmasqExitCode: The corresponding DNSMasq exit code.
        """
        if script_exit_code >= 11:
            return cls(script_exit_code - 10)
        else:
            raise ValueError("Invalid DNSMasq exit code")

class Action(Enum):
    START = 'start'
    RESTART = 'restart'
    STOP = 'stop'

class DNSMasqService(NetworkManager):
    """
    Class for controlling the DNSMasq demon service.

    """

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_SERVICE)
        
    def control_service(self, action: Action) -> bool:
        """
        Control the DNSMasq service.

        Args:
            action (Action): The action to perform (Action.START, Action.RESTART, or Action.STOP).

        Returns:
            bool: True if the service was controlled successfully, False otherwise.
        """
        if action not in Action:
            raise ValueError("Invalid action")

        cmd = ['systemctl', action.value, 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            self.log.error(f"Failed to {action.value} DNSMasq. Exit code: {cmd_result.exit_code}, Error: {cmd_result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
        
    def start_dnsmasq(self) -> bool:
        """
        Start the DNSMasq service.

        Returns:
            bool: True if the service started successfully, False otherwise.
        """
        cmd = ['systemctl', 'start', 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            self.log.error(f"Failed to start DNSMasq. Exit code: {cmd_result.exit_code}, Error: {cmd_result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def restart_dnsmasq(self) -> bool:
        """
        Restart the DNSMasq service.

        Returns:
            bool: True if the service restarted successfully, False otherwise.
        """
        cmd = ['systemctl', 'restart', 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            self.log.error(f"Failed to restart DNSMasq. Exit code: {cmd_result.exit_code}, Error: {cmd_result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def stop_dnsmasq(self) -> bool:
        """
        Stop the DNSMasq service.

        Returns:
            bool: True if the service stopped successfully, False otherwise.
        """
        cmd = ['systemctl', 'stop', 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            self.log.error(f"Failed to stop DNSMasq. Exit code: {cmd_result.exit_code}, Error: {cmd_result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    
    
class DNSMasqInterfaceService(DNSMasqService):
    """
    Class for controlling the DNSMasq Interface Service.

    Args:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration (default: False).

    Attributes:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration.

    Example:
        service = DNSMasqService("home", "192.168.1.0/24")
    """

    def __init__(self, dhcp_pool_name: str, dhcp_pool_subnet: str, negate=False):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_INTERFACE_SERVICE)
        
        self.dns_masq_config = DNSMasqConfigurator()
        
        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_subnet = dhcp_pool_subnet
        self.negate = negate
        self.dhcp_srv_db = DHCPServerDatabase()

    
    def build_interface_configuration(self) -> bool:
        """
        Build the interface configuration for DNSMasq.

        This method configures DNSMasq for the specified DHCP pool by setting the listen interfaces,
        DHCP pool ranges, and DHCP host reservations.

        Returns:
            bool: True if the configuration was successfully built, False otherwise.
        """

        # Get the interface names for the DHCP pool
        interface_names = self.dhcp_srv_db.get_dhcp_poll_interfaces_db(self.dhcp_pool_name)
        print(interface_names)
        '''
        # Set the listen interfaces in DNSMasq
        self.dns_masq_config.set_listen_interfaces(interface_names)

        # Get the DHCP pool ranges
        dhcp_pool_ranges = self.dhcp_srv_db.get_dhcp_pool_inet_range_db(self.dhcp_pool_name)

        # Enable DHCP server with netmask in DNSMasq
        for range_start, range_end, netmask in dhcp_pool_ranges:
            self.dns_masq_config.enable_dhcp_server_with_netmask(range_start, range_end, netmask)

        # Get the DHCP host reservations
        dhcp_hosts = self.dhcp_srv_db.get_dhcp_pool_reservation_db(self.dhcp_pool_name)

        # Add DHCP host reservations to DNSMasq
        for host in dhcp_hosts:
            if len(host) == 3:
                ethernet_address, ip_address, lease_time = host
                self.dns_masq_config.add_dhcp_host(ethernet_address, ip_address, lease_time)
            else:
                ethernet_address, ip_address = host
                self.dns_masq_config.add_dhcp_host(ethernet_address, ip_address)

        # Get DHCP pool options and add them to DNSMasq
        dhcp_pool_options = self.dhcp_srv_db.get_dhcp_pool_options_db(self.dhcp_pool_name)
        for option in dhcp_pool_options:
            option_code = DHCPOptionLookup.get_dhcpv4_option_code(option['Name'])
            if option_code is not None:
                self.dns_masq_config.add_dhcp_option(option_code, option['Value'])
        '''
        # Configuration built successfully
        return True


    
    def deploy_configuration(self) -> bool:
        return STATUS_OK
    
    def delete_configuration(self) -> bool:
        return STATUS_OK
    

class DNSMasqGlobalService(DNSMasqService):
    """
    Class for controlling the DNSMasq Interface Service.

    Args:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration (default: False).

    Attributes:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration.

    Example:
        service = DNSMasqService("home", "192.168.1.0/24")
    """

    def __init__(self, dhcp_pool_name: str, dhcp_pool_subnet: str, negate=False):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_INTERFACE_SERVICE)    
