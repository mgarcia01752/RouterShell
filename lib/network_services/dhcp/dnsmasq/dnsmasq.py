from enum import Enum, auto
import logging
import os
from shutil import copy
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.string_formats import StringFormats
from lib.db.dhcp_server_db import DHCPServerDatabase
from lib.network_manager.network_operations.network_mgr import NetworkManager
from lib.network_services.dhcp.common.dhcp_common import DHCPOptionLookup, DHCPVersion
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes, DNSMasqConfigurator
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

class DNSMasqDeploy(Enum):
    GLOBAL = auto()
    INTERFACE = auto()
    
class DNSMasqRunStatus(Enum):
    RUNNING = auto()
    STOPPED = auto()
    UNKNOWN = auto()

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
            bool: STATUS_OK if the service was controlled successfully, STATUS_NOK otherwise.
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
    """

    DNSMASQ_FILENAME_SUFFIX = '_dnsmasq.conf'
    DNSMASQ_GLOBAL_FILENAME = 'dnsmasq.conf'
    DNSMASQ_CONFIG_DIR = '/etc/dnsmasq.d'
    DEFAULT_LEASE_TIME = 86400
    DEFAULT_DNS_LISTEN_PORT=5353 # '''Setting DNS to 5353 prevents conflict if there is already DNS running'''

    def __init__(self, dhcp_pool_name: str, dhcp_pool_subnet: str, negate=False):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_INTERFACE_SERVICE)

        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_subnet = dhcp_pool_subnet
        self.negate = negate
                
        self.d_masq_if_config = DNSMasqConfigurator()
        self.d_masq_global_config = DNSMasqConfigurator()
        self.dhcp_srv_db = DHCPServerDatabase()
        self._build_global_configuration()

    def _build_global_configuration(self) -> bool:
        self.d_masq_global_config.add_listen_port(self.DEFAULT_DNS_LISTEN_PORT)
        return STATUS_OK
    
    def build_interface_configuration(self) -> bool:
        """
        Build the interface configuration for DNSMasq.

        This method configures DNSMasq for the specified DHCP pool by setting the listen interfaces,
        DHCP pool ranges, and DHCP host reservations.

        Returns:
            bool: STATUS_OK if the configuration was successfully built, STATUS_NOK otherwise.
        """
        # Get the interface names for the DHCP pool
        interface_names = self.dhcp_srv_db.get_dhcp_poll_interfaces_db(self.dhcp_pool_name)
        self.log.debug(f"Number of interfaces: {len(interface_names)} -> {interface_names[0]}")

        # Get the DHCP pool ranges
        dhcp_pool_ranges = self.dhcp_srv_db.get_dhcp_pool_inet_range_db(self.dhcp_pool_name)
        self.log.debug(dhcp_pool_ranges)

        # Get the DHCP host reservations
        dhcp_hosts = self.dhcp_srv_db.get_dhcp_pool_reservation_db(self.dhcp_pool_name)
        self.log.debug(dhcp_hosts)

        # Set the listen interfaces in DNSMasq
        for interface_name in interface_names:
            self.d_masq_if_config.set_listen_interfaces(list(interface_name.values()))

        if self.dhcp_srv_db.dhcp_pool_name_dhcp_version_db(self.dhcp_pool_name) == DHCPVersion.DHCP_V4:
            for entry in dhcp_pool_ranges:
                range_start, range_end, netmask = entry['inet_start'], entry['inet_end'], entry['inet_subnet']
                self.d_masq_if_config.add_dhcp4_range_with_netmask(range_start, range_end, netmask, self.DEFAULT_LEASE_TIME)
        
        else:
            for entry in dhcp_pool_ranges:
                
                StringFormats.modify_dict_value(entry, 'inet_subnet', '/', '')
                
                range_start, range_end, netmask = entry['inet_start'], entry['inet_end'], entry['inet_subnet']
                self.d_masq_if_config.add_dhcp6_range_with_prefix_len(range_start, range_end, int(netmask), self.DEFAULT_LEASE_TIME, DHCPv6Modes.SLAAC)            

        # Get DHCP pool options and add them to DNSMasq
        dhcp_pool_options = self.dhcp_srv_db.get_dhcp_pool_options_db(self.dhcp_pool_name)
        self.log.debug(f"DHCP-Pool-options: {dhcp_pool_options}")
        for option in dhcp_pool_options:
            
            self.log.debug(f"DHCP-Pool-option: {option} -> OPTION: {option['option']}")
            
            option_code = DHCPOptionLookup().get_dhcpv4_option_code(option['option'])
            
            if option_code is not None:
                self.d_masq_if_config.add_dhcp_option(option_code, option['value'])
        
        # Add DHCP host reservations to DNSMasq
        for host in dhcp_hosts:
            if len(host) == 3:
                ethernet_address, ip_address, lease_time = host.values()
                self.d_masq_if_config.add_dhcp_host(ethernet_address, ip_address, lease_time)
            else:
                ethernet_address, ip_address = host.values()
                self.d_masq_if_config.add_dhcp_host(ethernet_address, ip_address)               
        
        self.log.debug(self.d_masq_if_config.generate_configuration())
        
        return STATUS_OK
    
    def deploy_configuration(self, deploy_type: DNSMasqDeploy) -> bool:
        """
        Deploy the DNSMasq configuration.

        Args:
            deploy_type (DNSMasqDeploy): The type of DNSMasq configuration to deploy (DNSMasqDeploy.GLOBAL or DNSMasqDeploy.INTERFACE).

        Returns:
            bool: STATUS_OK if the configuration was successfully deployed, STATUS_NOK otherwise.
        """
        if deploy_type == DNSMasqDeploy.GLOBAL:
            configurator = self.d_masq_global_config
        elif deploy_type == DNSMasqDeploy.INTERFACE:
            configurator = self.d_masq_if_config
        else:
            raise ValueError("Invalid deployment type")

        # Generate the DNSMasq INTERFACE/GLOBAL configuration
        config_text = configurator.generate_configuration()

        if deploy_type == DNSMasqDeploy.GLOBAL:
            filename = f"{self.DNSMASQ_GLOBAL_FILENAME}"
        elif deploy_type == DNSMasqDeploy.INTERFACE:
            if not self.dhcp_pool_name:
                self.log.error("Unable to create DNSMasq Configuration, DHCP-pool undefined")
                return STATUS_NOK
            filename = f"{self.dhcp_pool_name}{self.DNSMASQ_FILENAME_SUFFIX}"
        else:
            raise ValueError("Invalid deployment type")

        destination_file = os.path.join(self.DNSMASQ_CONFIG_DIR, filename)

        if os.path.exists(destination_file):
            os.remove(destination_file)

        with open(destination_file, "w") as file:
            file.write(config_text)

        return STATUS_OK

    def clear_configurations(self) -> bool:
        """
        Clear DNSMasq configurations for the DHCP pool.

        Returns:
            bool: STATUS_OK if configurations were successfully cleared, STATUS_NOK otherwise.
        """
        config_dir = self.DNSMASQ_CONFIG_DIR
        
        if os.path.exists(config_dir) and os.is_dir(config_dir):
            try:
                for filename in os.listdir(config_dir):
                    if filename.endswith(self.DNSMASQ_FILENAME_SUFFIX):
                        file_path = os.path.join(config_dir, filename)
                        os.remove(file_path)
            except Exception as e:
                self.log.debug(f"Error while clearing configurations: {str(e)}")
                return STATUS_NOK

        return STATUS_OK

    def check_dnsmasq_status(self) -> DNSMasqRunStatus:
        """
        Check the status of DNSMasq using 'systemctl status dnsmasq' command.

        Returns:
            DNSMasqRunStatus: An enum representing the DNSMasq status - STOPPED, RUNNING, or UNKNOWN.
        """
        try:
            result = self.run(['systemctl', 'status', 'dnsmasq'])

            if result.exit_code:
                return DNSMasqRunStatus.STOPPED
            else:
                return DNSMasqRunStatus.RUNNING
        
        except Exception as e:
            self.log.error(f"Error: {str(e)}")
            return DNSMasqRunStatus.UNKNOWN

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
