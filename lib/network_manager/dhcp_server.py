import logging

from typing import Optional

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.db.dhcp_server_db import DHCPServerDatabase as DSD
from lib.network_manager.common.inet import InetServiceLayer, InetVersion
from lib.network_manager.network_manager import NetworkManager
from lib.network_services.dhcp.common.dhcp_common import DHCPVersion
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
        # TODO Allow only 1 IPv4 and 1 IPv6 DHCP subnet to support DUAL-STACK
        
        return DSD().update_dhcp_pool_name_interface(dhcp_pool_name, interface_name)

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