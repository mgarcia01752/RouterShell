import json
import logging
import os

from typing import Dict, Optional

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.db.dhcp_server_db import DHCPServerDatabase as DSD
from lib.network_manager.common.inet import InetServiceLayer, InetVersion
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_manager import NetworkManager
from lib.network_services.dhcp.common.dhcp_common import DHCPVersion
from lib.network_services.dhcp.dnsmasq.dnsmasq import Action, DNSMasqDeploy, DNSMasqInterfaceService
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSMasqConfigurator

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
        self.log.setLevel(RSLGS().DHCP_SERVER)
    
    def dhcp_pool_name_exists(self, dhcp_pool_name: str) -> bool:
        """
        Check if a DHCP pool with the given name exists.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to check.

        Returns:
            bool: True if the pool exists, False otherwise.
        """
        return DSD().dhcp_pool_name_exists_db(dhcp_pool_name)
    
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

    def add_dhcp_pool_to_interface(self, dhcp_pool_name: str, interface_name: str) -> bool:
        """
        Adds a DHCP pool to an interface.

        This method updates the DHCP pool name associated with a given interface.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add to the interface.
            interface_name (str): The name of the interface to associate with the DHCP pool.

        Returns:
            bool: True if the DHCP pool was successfully added to the interface, False otherwise.

        """
        
        # TODO Check interface IP address(es) are within the DHCP-pool-subnet range

        # Get inet-subnet-cidr from dhcp-pool-name == interface-inet-address -> subnet-range
        dhcp_pool_subnet = DSD().get_dhcp_pool_subnet_name_db(dhcp_pool_name)
        
        self.log.debug(f"add_dhcp_pool_to_interface() {dhcp_pool_name} -> {dhcp_pool_subnet}")
        
        DSD().update_dhcp_pool_name_interface(dhcp_pool_name, interface_name)

        DMIS = DNSMasqInterfaceService(dhcp_pool_name, dhcp_pool_subnet)
        
        if DMIS.build_interface_configuration():
            self.log.error(f"Unable to build DNSMasq Configuration")
            return STATUS_NOK
        
        if DMIS.deploy_configuration(DNSMasqDeploy.INTERFACE):
            self.log.error(f"Unable to set DNSMasq interface configuration")
            return STATUS_NOK
        
        if DMIS.control_service(Action.RESTART):
            self.log.error(f"Unable to restart DNSMasq")
            return STATUS_NOK    
        
        return STATUS_OK

class DhcpPoolFactory():
    ''''''
    def __init__(self, dhcp_pool_name: str):
        """
        Initialize the DhcpPoolFactory instance.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Raises:
            ValueError: If the provided subnet CIDR is invalid.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_POOL_FACTORY)
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
         
    def status(self) -> bool:
        """
        Get the status of the DhcpPoolFactory.

        Returns:
            bool: True if the factory status is OK, False otherwise.
        """
        return self.factory_status
    
    def add_pool_subnet(self, inet_subnet_cidr:str) -> bool:
        """
        Add a subnet to the DHCP pool.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add.

        Returns:
            bool: STATUS_OK if the subnet was added successfully, STATUS_NOK otherwise.
        """        
        if not self.status():
            self.log.error(f"Unable to add DHCP Pool subnet - ERROR: DhcpPoolFactory()")
            return STATUS_NOK        
        
        self.dhcp_pool_inet_subnet_cidr = inet_subnet_cidr
        
        return self.dhcp_srv_obj.add_dhcp_pool_subnet(self.dhcp_pool_name, inet_subnet_cidr)
        
    def add_inet_pool(self, inet_start: str, inet_end: str, inet_subnet_cidr: str) -> bool:
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
        

        return self.dhcp_srv_obj.add_dhcp_pool_subnet_inet_range(self.dhcp_pool_name,
                                                                 self.dhcp_pool_inet_subnet_cidr,
                                                                 inet_start, inet_end, inet_subnet_cidr)
    
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

import logging
import os
from typing import Dict

import logging
import os
import ipaddress
from typing import Dict, List, Union

class DhcpServerManager(RunCommand):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SERVER_MANAGER)

    def get_dhcp_lease_summary(self) -> Dict[str, List[Dict[str, Union[str, List[Dict[str, str]]]]]]:
        '''
        Get a summary of DHCP leases grouped by subnet.

        Returns:
            Dict: A hierarchical dictionary containing DHCP lease information.
                {
                    'subnet': [
                        {
                            "ip_address": str,
                            "mac_address": str,
                            "hostname": str,
                            "expires": str
                        },
                        ...
                    ],
                    ...
                }
        '''
        all_leases = self.get_all_leases()
        subnets = self.get_subnets_from_config()

        # Initialize the DHCP lease summary dictionary
        dhcp_lease_summary = {subnet: [] for subnet in subnets}

        # Group leases by subnet
        for lease in all_leases:
            for subnet in subnets:
                if self._is_ip_in_subnet(lease['ip_address'], subnet):
                    dhcp_lease_summary[subnet].append({
                        "ip_address": lease['ip_address'],
                        "mac_address": lease['mac_address'],
                        "hostname": lease['hostname'],
                        "expires": lease['expires'],
                    })
                    break  # Stop searching for other subnets once a match is found

        return dhcp_lease_summary

    def _is_ip_in_subnet(self, ip_address: str, subnet: str) -> bool:
        '''
        Check if an IP address belongs to a specified subnet.

        Args:
            ip_address (str): The IP address to check.
            subnet (str): The subnet in CIDR format.

        Returns:
            bool: True if the IP address belongs to the subnet, False otherwise.
        '''
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            network_obj = ipaddress.ip_network(subnet, strict=False)

            return ip_obj in network_obj
        except ValueError:
            # Handle invalid IP address or subnet
            return False

    def get_all_leases(self) -> List[Dict[str, str]]:
        try:
            leases_path = "/var/lib/misc/dnsmasq.leases"  # Modify this path based on your system
            if os.path.exists(leases_path):
                with open(leases_path, 'r') as leases_file:
                    leases_raw = leases_file.readlines()

                # Extract relevant fields from each lease entry
                leases = []
                for lease_raw in leases_raw:
                    lease_info = lease_raw.split()
                    # Check if the lease entry has the expected number of elements
                    if len(lease_info) >= 5:
                        subnet = lease_info[4]
                        if subnet != '*':
                            lease_dict = {
                                "ip_address": lease_info[2],
                                "mac_address": lease_info[1],
                                "hostname": lease_info[3],
                                "expires": lease_info[0],
                                "subnet": subnet,
                            }
                            leases.append(lease_dict)
                            print(f"Processed lease entry: {lease_dict}")
                        else:
                            print(f"Skipped lease entry due to wildcard subnet: {lease_info}")
                    else:
                        # Include malformed entries in the list with an indication
                        lease_dict = {
                            "malformed_entry": lease_raw.strip(),
                        }
                        leases.append(lease_dict)
                        print(f"Processed malformed lease entry: {lease_dict}")

                return leases

            else:
                self.log.warning(f"Leases file '{leases_path}' not found.")
                return []

        except Exception as e:
            self.log.error(f"Error retrieving DHCP leases: {e}")
            return []



    # Update get_subnets_from_config method
    def get_subnets_from_config(self, config_dir: str = "/etc/dnsmasq.d") -> List[str]:
        try:
            subnets = []
            
            # Check if the specified directory exists
            if os.path.exists(config_dir) and os.path.isdir(config_dir):
                # Iterate through all files in the specified directory
                for file_name in os.listdir(config_dir):
                    file_path = os.path.join(config_dir, file_name)
                    if os.path.isfile(file_path):
                        with open(file_path, 'r') as config_file:
                            config_lines = config_file.readlines()

                        # Process the lines in each file
                        for line in config_lines:
                            if line.startswith("dhcp-range="):
                                subnet = line.split(",")[1].strip()
                                subnets.append(subnet)
                                print(f"Found subnet in {file_name}: {subnet}")
            else:
                self.log.warning(f"Config directory '{config_dir}' not found or is not a directory.")

            # Log the subnets found
            subnet_log_str = ", ".join(subnets)
            self.log.info(f"Subnets found in {config_dir}: {subnet_log_str}")

            return subnets

        except Exception as e:
            self.log.error(f"Error retrieving subnets from config directory: {e}")
            return []


    def get_status(self) -> bool:
        return STATUS_OK
        
    def test_dhcp_server(self) -> bool:
        return STATUS_OK
    
    