import logging
import os

from typing import Dict, List

from lib.common.constants import DNSMASQ_LEASE_FILE_PATH
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.db.dhcp_server_db import DHCPServerDatabase as DSD
from lib.network_manager.common.inet import InetServiceLayer, InetVersion
from lib.network_manager.common.mac import MacServiceLayer
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_operations.network_mgr import NetworkManager
from lib.network_services.dhcp.common.dhcp_common import DHCPVersion
from lib.network_services.dhcp.dnsmasq.dnsmasq import DNSMasqDeploy, DNSMasqInterfaceService
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes
from lib.system.system_service_control.system_service_control import SysServCntrlAction


class InvalidDhcpServer(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class DHCPServer(NetworkManager):

    def __init__(self):
        """
        Initialize the DHCPServer instance.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SERVER)
    
    def dhcp_pool_name_exists(self, dhcp_pool_name: str) -> bool:
        """
        Check if a DHCP pool with the given name exists.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to check.

        Returns:
            bool: True if the pool exists, False otherwise.
        """
        return DSD().dhcp_pool_name_exists_db(dhcp_pool_name)

    def get_dhcp_pool_name_list(self) -> List[str]:
        """
        Retrieve a list of DHCP pool names from the DSD class.

        This method calls the dhcp_pool_name_list method from an instance
        of the DSD class to get the list of DHCP pool names.

        Returns:
            List[str]: A list of DHCP pool names.
        """
        return DSD().dhcp_pool_name_list()
    
    def dhcp_pool_subnet_exists(self, dhcp_pool_subnet_cidr: str) -> bool:
        """
        Check if a DHCP subnet within a DHCP pool exists.

        Args:
            dhcp_pool_subnet_cidr (str): The subnet CIDR to check.

        Returns:
            bool: True if the subnet exists, False otherwise.
        """
        return DSD().dhcp_pool_subnet_exist_db(dhcp_pool_subnet_cidr)
    
    def get_dhcp_pool_subnet(self, dhcp_pool_name:str) -> str:
        """
        Retrieve the DHCP pool subnet from the RouterShell database using the provided DHCP pool name.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            str: The DHCP pool subnet name retrieved from the RouterShell database.
            
        """        
        return DSD().get_dhcp_pool_subnet_name_db(dhcp_pool_name)
    
    def add_dhcp_pool_name(self, dhcp_pool_name: str) -> bool:
        """
        Add a DHCP pool name to the DHCP server if it does not already exist.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add.

        Returns:
            bool: STATUS_OK if the pool name was added successfully or already exists, STATUS_NOK otherwise.
        """
        if self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.debug(f"DHCP pool-name: {dhcp_pool_name}, already exists")
            return STATUS_OK

        return DSD().add_dhcp_pool_name_db(dhcp_pool_name)
    
    def del_dhcp_pool_name(self, dhcp_pool_name: str) -> bool:
        """
        Delete a DHCP pool by its name.
        
        Args:
            dhcp_pool_name (str): The name of the DHCP pool to be deleted.
        
        Returns:
            bool: STATUS_NOK if the DHCP pool does not exist, otherwise the status of the delete operation.
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.debug(f"DHCP pool-name: {dhcp_pool_name} does not exist")
            return STATUS_NOK
        return DSD().del_dhcp_pool_name(dhcp_pool_name)

    def add_dhcp_pool_subnet(self, dhcp_pool_name: str, dhcp_pool_subnet_cidr: str) -> bool:
        """
        Add a DHCP subnet to the DHCP server for the specified DHCP pool if it does not already exist.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add the subnet to.
            dhcp_pool_subnet_cidr (str): The subnet CIDR to add.

        Returns:
            bool: STATUS_OK if the subnet was added successfully or already exists, STATUS_NOK otherwise.
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add DHCP subnet to the DHCP server, dhcp-pool-name : {dhcp_pool_name} , does not exists")
            return STATUS_NOK
        
        if not self.is_valid_inet_subnet(dhcp_pool_subnet_cidr):
            self.log.error(f"Unable to add DHCP subnet to the DHCP server, subnet : {dhcp_pool_subnet_cidr} , is invalid subnet/CIDR")
            return STATUS_NOK
                    
        return DSD().add_dhcp_pool_subnet_db(dhcp_pool_name, dhcp_pool_subnet_cidr)
 
    def add_dhcp_pool_subnet_inet_range(self, dhcp_pool_name:str, 
                                        dhcp_pool_subnet_cidr: str, 
                                        inet_pool_start: str, 
                                        inet_pool_end: str, 
                                        inet_pool_subnet_cidr: str) -> bool:
        """
        Add an IP address range to a DHCP subnet within a DHCP pool.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.
            inet_dhcp_pool_subnet_cidr (str): The DHCP pool subnet CIDR.
            inet_pool_start (str): The starting IP address of the range.
            inet_pool_end (str): The ending IP address of the range.
            inet_pool_subnet_cidr (str): The subnet CIDR of the range.

        Returns:
            bool: STATUS_OK if the range was added successfully, STATUS_NOK otherwise
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add subnet pool inet range, dhcp-pool-name : {dhcp_pool_name} , does not exist")
            return STATUS_NOK

        if self.is_ip_range_within_subnet(dhcp_pool_subnet_cidr, inet_pool_start, inet_pool_end, inet_pool_subnet_cidr):
            self.log.error(f"inet pool range: ({inet_pool_start} - {inet_pool_end}) mask: {inet_pool_subnet_cidr} - "\
                           f"not within DHCP subnet-pool: {dhcp_pool_subnet_cidr}")
            return STATUS_NOK

        return DSD().add_dhcp_subnet_inet_address_range_db(dhcp_pool_subnet_cidr, 
                                                           inet_pool_start, 
                                                           inet_pool_end, 
                                                           inet_pool_subnet_cidr)
    
    def add_dhcp_pool_reservation(self, dhcp_pool_name: str, 
                                  inet_subnet_cidr: str, 
                                  hw_address: str, inet_address: str) -> bool:
        """
        Add a reservation to a DHCP pool.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.
            inet_subnet_cidr (str): The subnet CIDR of the reservation.
            hw_address (str): The MAC address for the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            bool: STATUS_OK if the reservation was added successfully, STATUS_NOK otherwise
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add a reservation to a DHCP pool, dhcp-pool-name : {dhcp_pool_name} , does not exist")
            return STATUS_NOK
        
        return DSD().add_dhcp_subnet_reservation_db(inet_subnet_cidr, hw_address, inet_address)
    
    def add_dhcp_pool_option(self, dhcp_pool_name: str, inet_subnet_cidr: str, dhcp_option: str, value: str) -> bool:
        """
        Add a DHCP option to a DHCP pool.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.
            inet_subnet_cidr (str): The subnet CIDR where the option is added.
            dhcp_option (str): The DHCP option to add.
            value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the option was added successfully, STATUS_NOK otherwise
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add DHCP option to a DHCP pool, dhcp-pool-name : {dhcp_pool_name} , does not exist")
            return STATUS_NOK

        return DSD().add_dhcp_subnet_option_db(inet_subnet_cidr, dhcp_option, value)

    def add_dhcp_pool_to_interface(self, dhcp_pool_name: str, interface_name: str, negate:bool=False) -> bool:
        """
        Adds a DHCP pool to an interface.

        This method updates the DHCP pool name associated with a given interface.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add to the interface.
            interface_name (str): The name of the interface to associate with the DHCP pool.

        Returns:
            bool: STATUS_OK if the DHCP pool was successfully added to the interface, STATUS_NOK otherwise.

        """
        
        # TODO Check interface IP address(es) are within the DHCP-pool-subnet range

        # Get inet-subnet-cidr from dhcp-pool-name == interface-inet-address -> subnet-range
        dhcp_pool_subnet = DSD().get_dhcp_pool_subnet_name_db(dhcp_pool_name)
        
        self.log.debug(f"add_dhcp_pool_to_interface() {dhcp_pool_name} -> {dhcp_pool_subnet}")
        
        DSD().update_dhcp_pool_name_interface(dhcp_pool_name, interface_name, negate)

        DMIS = DNSMasqInterfaceService(dhcp_pool_name, dhcp_pool_subnet)
        
        if negate:
            if DMIS.clear_configurations():
                self.log.error(f"Unable to remove DHCP Policy: {dhcp_pool_name} from router")
                return STATUS_NOK
            
            return STATUS_OK
        
        if DMIS.build_interface_configuration():
            self.log.error(f"Unable to build DNSMasq Configuration")
            return STATUS_NOK
        
        if DMIS.deploy_configuration(DNSMasqDeploy.INTERFACE):
            self.log.error(f"Unable to set DNSMasq interface configuration")
            return STATUS_NOK
        
        if DMIS.control_service(SysServCntrlAction.RESTART):
            self.log.error(f"Unable to restart DNSMasq")
            return STATUS_NOK    
        
        return STATUS_OK

    def update_dhcp_pool_mode(self, dhcp_pool_name: str, mode: DHCPv6Modes) -> bool:
        """
        Update the DHCP version mode for a specific DHCP pool.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool.
            mode (DHCPv6Modes): The DHCP version mode to set.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.

        This method checks if the specified DHCP pool exists. If the pool exists, it proceeds to update
        the DHCP version mode for that pool using the provided mode. If the update is successful,
        the method returns True; otherwise, it returns False.

        Note:
        - The DHCP pool's existence is verified using the `dhcp_pool_name_exists` method.
        - The actual update is performed by calling the `add_dhcp_subnet_option_db` method from the `DSD` class.

        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to update DHCP pool mode. DHCP pool name '{dhcp_pool_name}' does not exist.")
            return STATUS_NOK

        return DSD().update_dhcp_pool_mode_db(dhcp_pool_name, mode)

class DhcpPoolFactory():

    def __init__(self, dhcp_pool_name: str):
        """
        Initialize the DhcpPoolFactory instance.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Raises:
            ValueError: If the provided subnet CIDR is invalid.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_POOL_FACTORY)
        self.log.debug(f"Create DhcpPoolFactory({dhcp_pool_name}) ")
        
        self.factory_status = True
        
        self.dhcp_pool_name = None
        self.dhcp_pool_inet_subnet_cidr = None
                
        self.dhcp_srv_obj = DHCPServer()

        if not self.dhcp_srv_obj.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.debug(f"Adding dhcp-pool-name: {dhcp_pool_name} to DB")
            self.dhcp_srv_obj.add_dhcp_pool_name(dhcp_pool_name)

        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_inet_subnet_cidr = self.dhcp_srv_obj.get_dhcp_pool_subnet(dhcp_pool_name)
        self.log.debug(f"Create DhcpPoolFactory({dhcp_pool_name} , {self.dhcp_pool_inet_subnet_cidr}) ")

    def delete_pool_name(self) -> bool:
        """
        Delete a DHCP pool by its name.
                
        Returns:
            bool: The status of the delete operation.
        """
        return self.dhcp_srv_obj.del_dhcp_pool_name(self.dhcp_pool_name)

    def status(self) -> bool:
        """
        Get the status of the DhcpPoolFactory.

        Returns:
            bool: True if the factory status is OK, False otherwise.
        """
        return self.factory_status
    
    def add_pool_subnet(self, inet_subnet_cidr: str) -> bool:
        """
        Add a subnet to the DHCP pool.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add.

        Returns:
            bool: STATUS_OK if the subnet was added successfully, STATUS_NOK otherwise.
        """     

        is_valid, error_msg = InetServiceLayer.validate_subnet_format(inet_subnet_cidr)
        
        if not is_valid:
            self.log.error(f'Invalid subnet: {inet_subnet_cidr}. Error: {error_msg}')
            self._update_status(False)
            return STATUS_NOK

        if not self.status():
            self.log.error(f"Unable to add DHCP Pool subnet - ERROR: DhcpPoolFactory()")
            return STATUS_NOK        

        self.dhcp_pool_inet_subnet_cidr = inet_subnet_cidr

        if self.dhcp_srv_obj.add_dhcp_pool_subnet(self.dhcp_pool_name, inet_subnet_cidr):
            self.log.error(f"Failed to add subnet {inet_subnet_cidr} to the DHCP pool")
            return STATUS_NOK

        return STATUS_OK

    def add_inet_pool_range(self, inet_start: str, inet_end: str, inet_subnet_cidr: str) -> bool:
        """
        Add an IP address range to the DHCP pool.

        Args:
            inet_start (str): The starting IP address of the range.
            inet_end (str): The ending IP address of the range.
            inet_subnet_cidr (str): The subnet CIDR of the range.

        Returns:
            bool: STATUS_OK if the range was added successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error(f"Unable to add DHCP pool - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        if not InetServiceLayer.validate_inet_ranges(self.dhcp_pool_inet_subnet_cidr, inet_start, inet_end):
            self.log.error(f'Invalid IP Range [{self.dhcp_pool_inet_subnet_cidr} ->{inet_start} - {inet_end}]')
            return STATUS_NOK

        return self.dhcp_srv_obj.add_dhcp_pool_subnet_inet_range(
            self.dhcp_pool_name,
            self.dhcp_pool_inet_subnet_cidr,
            inet_start, inet_end, inet_subnet_cidr
        )

    def add_reservation(self, hw_address: str, inet_address: str) -> bool:
        """
        Add a reservation to the DHCP pool.

        Args:
            hw_address (str): The MAC address for the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            bool: STATUS_OK if the reservation was added successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error(f"Unable to add DHCP reservation - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        if not MacServiceLayer().is_valid_mac_address(hw_address) and not MacServiceLayer().is_valid_duid_ll(hw_address):
            self.log.error(f'Invalid hw-address: {hw_address}')    
            return STATUS_NOK
        
        if not InetServiceLayer.validate_inet_range(self.dhcp_pool_inet_subnet_cidr, inet_address):
            self.log.error(f'IP address not part of pool subnet [{self.dhcp_pool_inet_subnet_cidr} -> {inet_address}]')
            return STATUS_NOK

        return self.dhcp_srv_obj.add_dhcp_pool_reservation(self.dhcp_pool_name,
                                                           self.dhcp_pool_inet_subnet_cidr,
                                                           hw_address, inet_address)
    
    def add_option(self, dhcp_option: str, value: str) -> bool:
        """
        Add a DHCP option to the DHCP pool.

        Args:
            dhcp_option (str): The DHCP option to add.
            value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the option was added successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error(f"Unable to add DHCP options - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        return self.dhcp_srv_obj.add_dhcp_pool_option(self.dhcp_pool_name,
                                                      self.dhcp_pool_inet_subnet_cidr,
                                                      dhcp_option, value)

    def get_subnet_inet_version(self) -> DHCPVersion:
        """
        Determine the DHCP version (DHCPv4 or DHCPv6) based on the subnet's CIDR notation.

        Returns:
            DHCPVersion: An enum representing the DHCP version (DHCPv4, DHCPv6, or UNKNOWN).

        """
        if not self.dhcp_pool_inet_subnet_cidr:
            return DHCPVersion.UNKNOWN

        inet_version = InetServiceLayer().get_inet_subnet_inet_version(self.dhcp_pool_inet_subnet_cidr)

        if inet_version == InetVersion.IPv4:
            return DHCPVersion.DHCP_V4
        else:
            return DHCPVersion.DHCP_V6

    def add_dhcp_mode(self, mode: DHCPv6Modes) -> bool:
        """
        Update the DHCP mode for DHCPv6 subnets.

        This method allows updating the DHCP mode for DHCPv6 subnets. It checks the current status of the DHCP server,
        ensures it is in a valid state using `self.status()`, and then validates the DHCP version. If the DHCP version is 
        DHCPv4, it logs a debug message indicating that DHCP mode is reserved for DHCPv6 subnets and returns STATUS_NOK.

        Args:
            mode (DHCPv6Modes): The desired DHCP mode for DHCPv6 subnets.

        Returns:
            bool: STATUS_OK if the DHCP mode was updated successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error(f"Unable to update DHCP Mode - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        if self.get_subnet_inet_version() == DHCPVersion.DHCP_V4:
            self.log.debug(f'DHCP Mode is reserved for DHCPv6 subnet')
            return STATUS_NOK
        
        return self.dhcp_srv_obj.update_dhcp_pool_mode(self.dhcp_pool_name, mode)
        
    def _update_status(self, status: bool):
        """
        Update the status of the DhcpPoolFactory.

        This method is used to update the status of the DhcpPoolFactory. It takes a boolean parameter 'status' indicating
        whether the factory is in a valid state.

        Args:
            status (bool): The new status of the DhcpPoolFactory. True if the factory is in a valid state, False otherwise.

        Returns:
            None
        """
        self.factory_status = status


class DhcpServerManager(RunCommand):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SERVER_MANAGER)

    def get_leases(self) -> List[Dict[str, str]]:
        """
        Retrieve a list of DHCP leases from the dnsmasq leases file.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing lease information.
                Each dictionary has the following keys:
                - 'ip_address': The leased IP address.
                - 'mac_address': The MAC address of the device.
                - 'hostname': The hostname associated with the lease.
                - 'expires': The expiration timestamp of the lease.
        """        
        try:
            leases_path = DNSMASQ_LEASE_FILE_PATH

            if os.path.exists(leases_path):
                with open(leases_path, 'r') as leases_file:
                    leases_raw = leases_file.readlines()

                leases = []

                for lease_raw in leases_raw:
                    lease_info = lease_raw.split()
                    if len(lease_info) >= 5:
                        if "duid" not in lease_raw.lower():
                            lease_dict = {
                                "ip_address": lease_info[2],
                                "mac_address": lease_info[1],
                                "hostname": lease_info[3],
                                "expires": lease_info[0],
                            }
                            leases.append(lease_dict)
                            self.log.debug(f"Processed lease entry: {lease_dict}")
                    else:
                        lease_dict = {
                            "malformed_entry": lease_raw.strip(),
                        }
                        leases.append(lease_dict)
                        self.log.error(f"Processed malformed lease entry: {lease_dict}")

                return leases

            else:
                self.log.debug(f"Leases file '{leases_path}' not found.")
                return []

        except Exception as e:
            self.log.error(f"Error retrieving DHCP leases: {e}")
            return []
        
    def status(self) -> bool:
        """
        Get the status of dnsmasq.

        Returns:
            bool: STATUS_OK is active, otherwise STATUS_NOK

        """

        result = self.run(["systemctl", "is-active", "dnsmasq"])

        if result.exit_code:
            self.log.error(f"Error: Unable to get dnsmasq status. Exit code: {result.stderr}")
            return STATUS_NOK

        if result.stdout.strip() != 'active':
            self.log.debug(result.stdout)
            return STATUS_NOK

        return STATUS_OK

    def test_dhcp_server(self) -> bool:
        """
        Test the syntax of dnsmasq configuration files.

        Returns:
            bool: STATUS_OK if the syntax test is successful, STATUS_NOK otherwise.
        """

        result = self.run(["dnsmasq", "--test"])
        
        if result.exit_code:
            return STATUS_NOK
        
        self.log.debug(f"dnsmasq syntax test passed: {result.stdout}")
        return STATUS_OK

    def lease_log(self) -> List[str]:
        """
        Get the DHCP-related log entries from the system journal.

        Returns:
            List[str]: A list of DHCP-related log entries.
        """
        result = self.run(['journalctl | grep dnsmasq-dhcp'], shell=True, sudo=False)
        
        if result.exit_code:
            return []
        
        log_entries = result.stdout.split('\n')
        return log_entries

    def server_log(self) -> List[str]:
        """
        Get the DHCP-related log entries from the system journal.

        Returns:
            List[str]: A list of DHCP-related log entries.
        """
        command = 'journalctl | grep dnsmasq\\['

        result = self.run(["journalctl | grep 'dnsmasq\\['"], shell=True, sudo=False)
        
        if result.exit_code:
            return []
        
        log_entries = result.stdout.split('\n')
        return log_entries

 