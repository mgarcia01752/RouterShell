import copy
import ipaddress
import json
import logging
from typing import Dict, Union

from lib.common.common import STATUS_NOK, STATUS_OK

from enum import Enum
class DhcpVersion(Enum):
    DHCP_V4 = 4
    DHCP_V6 = 6

class DHCPDatabaseFactory():
    
    def __init__(self, 
                 dhcp_pool_name: str, 
                 ip_subnet_mask: ipaddress.IPv4Network,
                 negate=False):
        
        self.log = logging.getLogger(self.__class__.__name__)

        self.dhcp_pool_name = dhcp_pool_name
        self.ip_subnet_mask = ip_subnet_mask
        
        self.log.debug(f"DHCPDatabaseFactory() -> dhcp_pool_name: {self.dhcp_pool_name} -> ip_subnet_mask: {self.ip_subnet_mask}")
        
        self.dhcp_version = DhcpVersion.DHCP_V4

        if not DHCPDatabase().pool_name_exists(dhcp_pool_name):
            
            pool_name_id = DHCPDatabase().get_pool_name_id(dhcp_pool_name)
            
            self.dhcp_pool_db = DHCPDatabase().get_dhcp_pool()
            print(f"DHCP-POOL-DB: {self.dhcp_pool_db}")
                
            self.kea_v4_db = DHCPDatabase().get_kea_config()
            print(f"KEA-DB: {self.kea_v4_db}")
        
            if negate:
                self.log.debug(f"Removing DHCP pool: {dhcp_pool_name}")
                
                # Delete pool-name
                if DHCPDatabase().delete_pool_name(dhcp_pool_name):
                    self.log.error(f"Unable to delete DHCP pool name: {dhcp_pool_name}")
                    return STATUS_NOK
                
                # Delete subnet associated to pool-name
                if DHCPDatabase().delete_subnet(pool_name_id):
                    self.log.error(f"Unable to delete or does not exists DHCP Subnet-ID: {pool_name_id}")
                    return STATUS_NOK
                
                self.log.debug(f"Remove references pointers to preserve db")
                self.kea_v4_db, self.dhcp_pool_db = None

            else:                    
                self.subnet_id = (DHCPDatabase().get_number_of_subnets(self.dhcp_version) + 1)
                
                if self._set_pool_name(dhcp_pool_name, self.subnet_id):
                    self.log.error(f"Unable to add DHCP Pool {dhcp_pool_name}")
                else:
                    self._set_subnet(ip_subnet_mask, self.dhcp_version, self.subnet_id)  
        else:
            pass

    def _set_pool_name(self, pool_name: str, subnet_id: int = -1) -> bool:
        """
        Add a pool name to the DHCP configuration and associate it with a subnet ID.

        Args:
            pool_name (str): The name of the pool to add.
            subnet_id (int): The ID of the subnet to associate the pool with.
                Default subnet_id = -1, if subnet ID is not know at the time of add

        Returns:
            bool: STATUS_OK if the pool name was added successfully, STATUS_NOK if it already exists.
        """
        # Check if the pool name already exists
        for pool_entry in self.dhcp_pool_db["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return STATUS_NOK

        # If the pool name doesn't exist, add it
        new_pool_entry = {
            "subnet-id": subnet_id,
            "name": pool_name
        }
        self.dhcp_pool_db["DhcpPool"]["pool-name"].append(new_pool_entry)
        return STATUS_OK
        
    def _set_subnet(self, ip_subnet_mask: ipaddress.IPv4Network, dhcp_version: int, subnet_id: int = 0) -> bool:
        """
        Add a new subnet to the DHCP configuration.

        Args:
            ip_subnet_mask (ipaddress.IPv4Network): The IPv4 subnet and mask in CIDR notation (e.g., "192.168.1.0/24").
            dhcp_version (int): The DHCP version (e.g., 4 for DHCPv4 or 6 for DHCPv6).
            subnet_id (int, optional): The ID of the subnet you're adding. If not provided, it will be automatically assigned based on existing subnets.

        Returns:
            bool: STATUS_OK if the subnet was successfully added to the configuration, STATUS_NOK otherwise.
        """
        if not subnet_id:
            subnet_id = (DHCPDatabase.get_number_of_subnets(dhcp_version) + 1)

        new_subnet = {
            "id": subnet_id,
            "subnet": str(ip_subnet_mask)
        }

        # Add the new subnet to the existing configuration
        self.kea_v4_db["Dhcp4"]["subnet4"].append(new_subnet)

        return STATUS_OK

    def get_subnet_pool_ID(self):
        """
        Get the ID of the subnet associated with the DHCP pool.

        Returns:
            int: The ID of the subnet, or -1 if no subnet is associated.
        """
        if hasattr(self, 'subnet_id'):
            return self.subnet_id
        else:
            self.log.error("No subnet associated with the DHCP pool.")
            return -1
    
    def get_subnet_pool(self):
        """
        Get the subnet for the DHCP pool.

        Returns:
            ipaddress.IPv4Network or ipaddress.IPv6Network: The subnet in CIDR notation.
            None: If the subnet is not defined or an error occurs.
        """
        try:
            if self.ip_subnet_mask is not None:
                return self.ip_subnet_mask
            else:
                self.log.error("Subnet is not defined.")
        except Exception as e:
            self.log.error(f"Error while getting the subnet: {str(e)}")
        
        return None

    def add_pool(self, pool_id: int, ip_address_start, ip_address_end, subnet_mask):
        """
        Add a new IP address pool to the DHCP configuration, supporting both IPv4 and IPv6.

        Args:
            pool_id (int): The ID of the pool to be added.
            ip_address_start (str): The start IP address of the pool.
            ip_address_end (str): The end IP address of the pool.
            subnet_mask (str): The subnet mask in CIDR notation (e.g., "24" for a /24 subnet).

        Returns:
            bool: STATUS_OK if the pool was successfully added, STATUS_NOK if there was an error.
        """
        subnet_pool = self.get_subnet_pool()  # Check if a subnet is defined
        if subnet_pool is None:
            self.log.error("Cannot add a pool. Subnet is not defined.")
            return STATUS_NOK
        
        try:
            ip_subnet_pool = ipaddress.ip_address(subnet_pool)
            ip_start = ipaddress.ip_address(ip_address_start)
            ip_end = ipaddress.ip_address(ip_address_end)

            if ip_start.version == ip_end.version == ip_subnet_pool.version:
                
                dhcp_version = DhcpVersion.DHCP_V4 if subnet_pool.version == 4 else DhcpVersion.DHCP_V6
                subnet_key = f"subnet{dhcp_version}"
                
                if ip_subnet_pool.network_address <= ip_start <= ip_end <= ip_subnet_pool.broadcast_address:
                    
                    subnet_pool_id = self.get_subnet_pool_ID()

                    # Create the dhcp pool entry
                    dhcp_pool_entry = {
                        "pool": f"{ip_address_start} - {ip_address_end}",
                        "option-data": f"[subnet-mask: {subnet_mask}]"
                    }
                                   
                    if "pools" not in self.kea_v4_db["Dhcp4"][subnet_key][subnet_pool_id]:
                        self.log.debug(f"add_pool() -> pools entry not found -> adding pools array entry")
                        self.kea_v4_db["Dhcp4"][subnet_key][subnet_pool_id]["pools"] = []

                    self.kea_v4_db["Dhcp4"][subnet_key][subnet_pool_id]["pools"].append(pool_entry)

                    # Add the pool_id entry to dhcp_pool_db
                    dhcp_pool_entry = {
                        "pool-id": pool_id,
                        "pool-name": pool_name
                    }
                    self.dhcp_pool_db["DhcpPool"]["pool-name"].append(pool_entry)

                    return STATUS_OK
                else:
                    self.log.error("IP address range is not within the specified subnet.")
            else:
                self.log.error("Invalid IP address types. Ensure they are all IPv4 or IPv6.")
        except (ipaddress.AddressValueError, ValueError):
            self.log.error("Invalid IP address or subnet mask format.")

        return STATUS_NOK


class DHCPDatabase:
    """
    DHCPDatabase class for managing DHCP configuration.
    """

    dhcp_pool_default = {
        "DhcpPool": {
            "pool-name": [
                {
                    "name" : "dhcp-pool-1",
                    "pools" : [
                        {
                            "id" : 0,
                            "subnet-range": "",
                        }
                    ]
                }
            ]     
        }
    }
        
    dhcp_pool = {
        "DhcpPool": {
            "pool-name": [
            ]
        }
    }

    kea_v4_db = {
        "Dhcp4": {
            "valid-lifetime": 4000,
            "renew-timer": 1000,
            "rebind-timer": 2000,
            "interfaces-config": {
                "interfaces": [""],
                "service-sockets-max-retries": 5,
                "service-sockets-retry-wait-time": 5000
            },
            "lease-database": {
                "type": "memfile",
                "persist": True,
                "name": "/var/lib/kea/dhcp4.leases"
            },
            "subnet4": []
        }
    }
 
    kea_v6_db = {
        "Dhcp6": {
            "valid-lifetime": 4000,
            "renew-timer": 1000,
            "rebind-timer": 2000,
            "interfaces-config": {
                "interfaces": [""],
                "service-sockets-max-retries": 5,
                "service-sockets-retry-wait-time": 5000
            },
            "lease-database": {
                "type": "memfile",
                "persist": True,
                "name": "/var/lib/kea/dhcp4.leases"
            },
            "subnet6": []
        }
    }
    
    def __init__(self, config_file: str = None):
        """
        Initialize the DHCPDatabase instance.

        Args:
            config_file (str, optional): The path to the DHCP configuration file.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file

    def add_subnet(self, subnet_id: int, subnet_range: str, client_class: str="", relay_ip: str=""):
        """
        Add a subnet to the DHCP configuration.

        Args:
            subnet_id (int): The unique ID of the subnet.
                pass
        subnet_range (str): The range of IP addresses for the subnet.
            client_class (str): The client class for the subnet.
            relay_ip (str): The IP address of the relay agent for the subnet.
        """
        # Create a new subnet configuration
        new_subnet = {
            "id": subnet_id,
            "subnet": subnet_range,
            "pools": [],
            "client-class": client_class,
            "relay": {
                "ip-addresses": [relay_ip]
            }
        }

        # Add the new subnet to the existing configuration
        self.kea_v4_db["Dhcp4"]["subnet4"].append(new_subnet)

    def add_reservation_to_subnet(self, subnet_id: int, mac: str, ip: str, hostname: str = ""):
        """
        Add a reservation to a subnet.

        Args:
            subnet_id (int): The ID of the subnet to add the reservation to.
            mac (str): The MAC address of the reserved client.
            ip (str): The reserved IP address.
            hostname (str, optional): The hostname for the reserved client.
        """
        ip_address = ipaddress.IPv4Address(ip)

        new_reservation = {
            "hw-address": mac,
            "ip-address": str(ip_address),  # Convert the IP address back to a string
            "hostname": hostname
        }

        # Find the subnet with the given ID
        for subnet in self.kea_v4_db["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                # Append the new reservation to the reservations list in the pool
                subnet["pools"][0]["reservations"].append(new_reservation)
                break  # Exit the loop once the subnet is found

    def add_pool_to_subnet(self, subnet_id: int, ip_pool_start: str, ip_pool_end: str):
        """
        Add an IP pool to a subnet.

        Args:
            subnet_id (int): The ID of the subnet to add the pool to.
            ip_pool_start (str): The start IP address of the pool.
            ip_pool_end (str): The end IP address of the pool.
        """
        # Find the subnet with the given ID
        for subnet in self.kea_v4_db["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                # Create a new pool configuration
                new_pool = {
                    "pool": f"{ip_pool_start} - {ip_pool_end}",
                    "reservations": []
                }
                # Append the new pool to the subnet's pools list
                subnet["pools"].append(new_pool)
                break  # Exit the loop once the subnet is found

    def add_pool_name(self, pool_name: str, subnet_id: int = -1) -> bool:
        """
        Add a pool name to the DHCP configuration and associate it with a subnet ID.

        Args:
            pool_name (str): The name of the pool to add.
            subnet_id (int): The ID of the subnet to associate the pool with.
                Default subnet_id = -1, if subnet ID is not know at the time of add

        Returns:
            bool: STATUS_OK if the pool name was added successfully, STATUS_NOK if it already exists.
        """
        # Check if the pool name already exists
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return STATUS_NOK  # Pool name already exists

        # If the pool name doesn't exist, add it
        new_pool_entry = {
            "subnet-id": subnet_id,
            "name": pool_name
        }
        self.dhcp_pool["DhcpPool"]["pool-name"].append(new_pool_entry)
        return STATUS_OK  # Pool name added successfully

    def update_pool_name(self, pool_name: str, new_subnet_id: int) -> bool:
        """
        Update the subnet ID associated with a pool name in the DHCP configuration.

        Args:
            pool_name (str): The name of the pool to update.
            new_subnet_id (int): The new subnet ID to associate with the pool.

        Returns:
            bool: STATUS_OK if the pool name was updated successfully, STATUS_NOK if the pool name doesn't exist.
        """
        # Find the pool entry by name
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                # Update the subnet ID
                pool_entry["subnet-id"] = new_subnet_id
                return STATUS_OK  # Pool name updated successfully

        # If the pool name doesn't exist, return False
        return STATUS_NOK

    def get_number_of_subnets(self, dhcp_version: DhcpVersion = DhcpVersion.DHCP_V4) -> int:
        """
        Get the number of subnets based on the DHCP version.

        Args:
            dhcp_version (DhcpVersion, optional): Enum representing the DHCP version (DhcpVersion.DHCPv4 or DhcpVersion.DHCPv6).
                Defaults to DhcpVersion.DHCPv4.

        Returns:
            int: The number of subnets based on the specified DHCP version.
        """
        # Determine the appropriate key based on the DHCP version
        subnet_key = "subnet4" if dhcp_version == DhcpVersion.DHCP_V4 else "subnet6"
        
        self.log.debug(f"get_number_of_subnets() -> dhcp-version: {dhcp_version} -> Key: {subnet_key}")

        # Check if the specified key exists in the configuration
        if subnet_key in self.kea_v4_db["Dhcp4"]:
            return len(self.kea_v4_db["Dhcp4"][subnet_key])
        else:
            return 0

    def pool_name_exists(self, pool_name: str) -> bool:
        """
        Check if a pool name exists in the DHCP configuration.

        Args:
            pool_name (str): The pool name to check.

        Returns:
            bool: True if the pool name exists, False otherwise.
        """
        # Check if the pool name exists
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return True  # Pool name exists
        return False  # Pool name does not exist

    def update_global_config(self, dhcp_option: str, value: Union[str, int, bool], dhcp_version: int = 0):
        """
        Update a key-value pair in the global DHCP configuration.

        Args:
            dhcp_option (str): The DHCP option to update in the global configuration.
            value (Union[str, int, bool]): The new value for the DHCP option.
            dhcp_version (int, optional): 0 for DHCPv4, 1 for DHCPv6.

        Raises:
            ValueError: If the specified DHCP version is invalid.
        """
        # Check if the DHCP version is valid
        if dhcp_version not in [0, 1]:
            raise ValueError("Invalid DHCP version. Use 0 for DHCPv4 or 1 for DHCPv6.")

        # Get the appropriate DHCP configuration based on the version
        dhcp_config = self.kea_v4_db if dhcp_version == 0 else self.kea_dhcpv6_config

        # Check if the key exists in the global configuration
        if dhcp_option in dhcp_config["Dhcp4"]:
            dhcp_config["Dhcp4"][dhcp_option] = value
        else:
            # Append the new key-value pair to the global configuration
            dhcp_config["Dhcp4"][dhcp_option] = value

    def save_config_to_file(self):
        """
        Save the current DHCP configuration to the specified configuration file.
        """
        # Save the updated configuration back to the file
        with open(self.config_file, 'w') as file:
            json.dump(self.kea_v4_db, file, indent=4)

    def get_copy_dhcp_pool(self) -> str:
        """
        Get a deep copy of the DHCP pool configuration as a JSON string.

        Returns:
            str: A JSON string representing the DHCP pool configuration.
        """
        return json.dumps(self.dhcp_pool)

    def get_copy_kea_dhcpv4_config(self) -> str:
        """
        Get a deep copy of the KEA DHCPv4 configuration as a JSON string.

        Returns:
            str: A JSON string representing the KEA DHCPv4 configuration.
        """
        return json.dumps(self.kea_v4_db)
    
    def get_dhcp_pool(self):
        """
        Get the DHCP pool configuration.

        Returns:
            dict: The DHCP pool configuration.
        """
        return self.dhcp_pool

    def get_kea_config(self):
        """
        Get the Kea DHCPv4 configuration.

        Returns:
            dict: The Kea DHCPv4 configuration.
        """
        return self.kea_v4_db

    def delete_pool_name(self, pool_name:str) -> bool:
        """
        Delete a DHCP pool by name.

        Args:
            pool_name (str): The name of the DHCP pool to delete.

        Returns:
            bool: STATUS_OK if the pool was successfully deleted, STATUS_NOK if the pool was not found.
        """
        if pool_name in self.dhcp_pool["DhcpPool"]["pool-name"]:
            self.dhcp_pool["DhcpPool"]["pool-name"].remove(pool_name)
            return STATUS_OK
        return STATUS_NOK

    def delete_subnet(self, subnet_id: int) -> bool:
        """
        Delete a DHCP subnet by ID.

        Args:
            subnet_id (int): The ID of the DHCP subnet to delete.

        Returns:
            bool: STATUS_OK if the subnet was successfully deleted, STATUS_NOK if the subnet was not found.
        """
        for subnet in self.kea_v4_db["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                self.kea_v4_db["Dhcp4"]["subnet4"].remove(subnet)
                return STATUS_OK
        return STATUS_NOK

    def get_pool_name_id(self, pool_name:str) -> int:
        """
        Get the ID of a DHCP pool by its name.

        Args:
            pool_name (str): The name of the DHCP pool to retrieve the ID for.

        Returns:
            int: The ID of the DHCP pool if found, or None if the pool was not found, Error = -1.
        """
        if not pool_name:
            self.log.error(f"get_pool_name_id -> {pool_name}")
            return -1
        
        pool_names = self.dhcp_pool["DhcpPool"]["pool-name"]
        if pool_name in pool_names:
            return pool_names.index(pool_name)
        return None

class DhcpOptionsLUT:
    '''https://kea.readthedocs.io/en/latest/arm/dhcp4-srv.html#interface-configuration'''
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.dhcp_options = {
            "time-offset": "int",
            "routers": "ipaddress",
            "time-servers": "ipaddress",
            "name-servers": "ipaddress",
            "domain-name-servers": "ipaddress",
            "log-servers": "ipaddress",
            "cookie-servers": "ipaddress",
            "lpr-servers": "ipaddress",
            "impress-servers": "ipaddress",
            "resource-location-servers": "ipaddress",
            "boot-size": "int",
            "merit-dump": "string",
            "domain-name": "fqdn",
            "swap-server": "ipaddress",
            "root-path": "string",
            "extensions-path": "string",
            "ip-forwarding": "boolean",
            "non-local-source-routing": "boolean",
            "policy-filter": "ipaddress",
            "max-dgram-reassembly": "int",
            "default-ip-ttl": "int",
            "path-mtu-aging-timeout": "int",
            "path-mtu-plateau-table": "int",
            "interface-mtu": "int",
            "all-subnets-local": "boolean",
            "broadcast-address": "ipaddress",
            "perform-mask-discovery": "boolean",
            "mask-supplier": "boolean",
            "router-discovery": "boolean",
            "router-solicitation-address": "ipaddress",
            "static-routes": "ipaddress",
            "trailer-encapsulation": "boolean",
            "arp-cache-timeout": "int",
            "ieee802-3-encapsulation": "boolean",
            "default-tcp-ttl": "int",
            "tcp-keepalive-interval": "int",
            "tcp-keepalive-garbage": "boolean",
            "nis-domain": "string",
            "nis-servers": "ipaddress",
            "ntp-servers": "ipaddress",
            "vendor-encapsulated-options": "empty",
            "netbios-name-servers": "ipaddress",
            "netbios-dd-server": "ipaddress",
            "netbios-node-type": "int",
            "netbios-scope": "string",
            "font-servers": "ipaddress",
            "x-display-manager": "ipaddress",
            "dhcp-option-overload": "int",
            "dhcp-server-identifier": "ipaddress",
            "dhcp-message": "string",
            "dhcp-max-message-size": "int",
            "vendor-class-identifier": "string",
            "nwip-domain-name": "string",
            "nwip-suboptions": "binary",
            "nisplus-domain-name": "string",
            "nisplus-servers": "ipaddress",
            "tftp-server-name": "string",
            "boot-file-name": "string",
            "mobile-ip-home-agent": "ipaddress",
            "smtp-server": "ipaddress",
            "pop-server": "ipaddress",
            "nntp-server": "ipaddress",
            "www-server": "ipaddress",
            "finger-server": "ipaddress",
            "irc-server": "ipaddress",
            "streettalk-server": "ipaddress",
            "streettalk-directory-assistance-server": "ipaddress",
            "user-class": "binary",
            "slp-directory-agent": "record (boolean, ipaddress)",
            "slp-service-scope": "record (boolean, string)",
            "nds-server": "ipaddress",
            "nds-tree-name": "string",
            "nds-context": "string",
            "bcms-controller-names": "fqdn",
            "bcms-controller-address": "ipaddress",
            "client-system": "int",
            "client-ndi": "record (int, int, int)",
            "uuid-guid": "record (int, binary)",
            "uap-servers": "string",
            "geoconf-civic": "binary",
            "pcode": "string",
            "tcode": "string",
            "v6-only-preferred": "int",
            "netinfo-server-address": "ipaddress",
            "netinfo-server-tag": "string",
            "v4-captive-portal": "string",
            "auto-config": "int",
            "name-service-search": "int",
            "domain-search": "fqdn",
            "vivco-suboptions": "record (int, binary)",
            "vivso-suboptions": "int",
            "pana-agent": "ipaddress",
            "v4-lost": "fqdn",
            "capwap-ac-v4": "ipaddress",
            "sip-ua-cs-domains": "fqdn",
            "v4-sztp-redirect": "tuple",
            "rdnss-selection": "record (int, ipaddress, ipaddress, fqdn)",
            "v4-portparams": "record (int, psid)",
            "v4-dnr": "record (int, int, int, fqdn, binary)",
            "option-6rd": "record (int, int, ipv6-address, ipaddress)",
            "v4-access-domain": "fqdn"
        }

    def dhcp_option_exists(self, dhcp_option: str) -> bool:
        """
        Verify if DHCP option exists in the DHCP configuration options.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return dhcp_option in self.dhcp_options

    def get_data_type(self, dhcp_option: str) -> Union[None, str]:
        """
        Get the data type associated with a key in the DHCP configuration options.

        Args:
            key (str): The key to retrieve the data type for.

        Returns:
            Union[None, str]: The data type of the key, or None if the key does not exist.
        """
        if self.dhcp_option_exists(dhcp_option):
            return self.dhcp_options[dhcp_option]
        else:
            return None

