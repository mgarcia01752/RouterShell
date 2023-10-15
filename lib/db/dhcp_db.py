import copy
import ipaddress
import json
import logging
from typing import Dict, Union
from lib.common.constants import STATUS_NOK, STATUS_OK

from enum import Enum
class DhcpVersion(Enum):
    DHCP_V4 = 4
    DHCP_V6 = 6

class KeaDHCPDBFactory():
    def __init__(self, dhcp_pool_name: str, ip_subnet_mask: str, negate=False):
        self.log = logging.getLogger(self.__class__.__name__)

        try:
            # Attempt to create an IPv4Network or IPv6Network object from the provided subnet string
            self.ip_subnet_mask = ipaddress.ip_network(ip_subnet_mask, strict=False)
            self.log.info(f"Subnet: {self.ip_subnet_mask}")
        except ValueError:
            self.log.error("Invalid subnet format. Please provide a valid subnet in CIDR notation.")
            raise ValueError("Invalid subnet format. Please provide a valid subnet in CIDR notation.")

        self.dhcp_pool_name = dhcp_pool_name
        self.negate = negate

        self.kea_db_obj = KeaDHCPDB()

        # check to see if both dhcp_pool_name and ip_subnet_mask does not exist
       
class KeaDHCPDB():
    
    dhcp_pool_db = {
        "DhcpPoolDB": {
            "pool_names": []
        }
    }
    
    '''KEA DHCPv4 CONFIGURATION'''
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

    '''KEA DHCPv6 CONFIGURATION'''
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
                "name": "/var/lib/kea/dhcp6.leases"
            },
            "subnet6": []
        }
    }

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def pool_name_exists(self, pool_name: str) -> bool:
        """
        Check if a pool name exists in the database.

        Args:
            pool_name (str): The name of the pool to check.

        Returns:
            bool: STATUS_OK if the pool name exists, STATUS_NOK otherwise.
        """
        return any(pool["name"] == pool_name for pool in self.dhcp_pool_db.get("DhcpPoolDB", {}).get("pool_names", []))

    def add_pool_name(self, id: int, pool_name: str, dhcp_version: DhcpVersion) -> bool:
        """
        Add a pool name to the database.

        Args:
            id (int): The ID of the pool.
            pool_name (str): The name of the pool.
            dhcp_version (DhcpVersion): The DHCP version (DhcpVersion.DHCP_V4 or DhcpVersion.DHCP_V6).

        Returns:
            bool: STATUS_OK if the pool name was added, STATUS_NOK otherwise.
        """
        self.log.info(f"add_pool_name() -> {pool_name} -> DHCP-Version: {dhcp_version}")
        
        if not self.pool_name_exists(pool_name):
            pool_data = {
                "id": id,
                "name": pool_name,
                "dhcp_version": dhcp_version.value  # Convert to the enum value.
            }
            self.dhcp_pool_db["DhcpPoolDB"]["pool_names"].append(pool_data)
            return STATUS_OK
        else:
            self.log.warning(f"Pool name '{pool_name}' already exists.")
            return STATUS_NOK

    def get_num_of_subnets(self, dhcp_version: DhcpVersion) -> int:
        """
        Get the number of subnets for a specific DHCP version.

        Args:
            dhcp_version (DhcpVersion): The DHCP version (DhcpVersion.DHCP_V4 or DhcpVersion.DHCP_V6).

        Returns:
            int: The number of subnets.
        """
        self.log.info(f"get_num_of_subnets() -> {dhcp_version}")
        
        if dhcp_version == DhcpVersion.DHCP_V4:
            return len(self.kea_v4_db["Dhcp4"]["subnet4"])
        elif dhcp_version == DhcpVersion.DHCP_V6:
            return len(self.kea_v6_db["Dhcp6"]["subnet6"])
        else:
            self.log.error(f"Invalid DHCP version: {dhcp_version}")
            return 0

    def set_subnet(self, ip_subnet: str, dhcp_version: DhcpVersion) -> bool:
        """
        Set a subnet for a specific DHCP version.

        Args:
            ip_subnet (str): The IP subnet in string format.
            dhcp_version (DhcpVersion): The DHCP version (DhcpVersion.DHCP_V4 or DhcpVersion.DHCP_V6).

        Returns:
            bool: STATUS_OK if the subnet was added, STATUS_NOK otherwise.
        """
        self.log.info(f"set_subnet() -> {ip_subnet} -> {dhcp_version}")
        try:
            if dhcp_version == DhcpVersion.DHCP_V4:
                self.kea_v4_db["Dhcp4"]["subnet4"].append({"subnet": ip_subnet})
            elif dhcp_version == DhcpVersion.DHCP_V6:
                self.kea_v6_db["Dhcp6"]["subnet6"].append({"subnet": ip_subnet})
            else:
                self.log.error(f"Invalid DHCP version: {dhcp_version}")
                return STATUS_NOK
            return STATUS_OK
        except Exception as e:
            self.log.error(f"Failed to set subnet: {str(e)}")
            return STATUS_NOK

    def get_user_context_dm(self):
        '''Get a copy of the user-context Data Model'''
        context_data = {
            "user-context": {}
        }
        return context_data
        
    def add_user_context(self, dhcp_version: DhcpVersion, subnet_id: int, user_context: dict) -> bool:
        """
        Add user context data to a specific subnet.

        Args:
            dhcp_version (DhcpVersion): The DHCP version (DhcpVersion.DHCP_V4 or DhcpVersion.DHCP_V6).
            subnet_id (int): The ID of the subnet to add user context to.
            user_context (dict): The user context data to add.

            context_data = {
                "user-context": {
                    "comment": "second floor",
                    "meta-date": {...[...]...}
            }

        Returns:
            bool: STATUS_OK if user context was added, STATUS_NOK otherwise.
        """
        try:
            if dhcp_version == DhcpVersion.DHCP_V4:
                if subnet_id < len(self.kea_v4_db["Dhcp4"]["subnet4"]):
                    self.kea_v4_db["Dhcp4"]["subnet4"][subnet_id]["user-context"] = user_context
                else:
                    self.log.error(f"Invalid subnet ID: {subnet_id}")
                    return STATUS_NOK
            elif dhcp_version == DhcpVersion.DHCP_V6:
                if subnet_id < len(self.kea_v6_db["Dhcp6"]["subnet6"]):
                    self.kea_v6_db["Dhcp6"]["subnet6"][subnet_id]["user-context"] = user_context
                else:
                    self.log.error(f"Invalid subnet ID: {subnet_id}")
                    return STATUS_NOK
            else:
                self.log.error(f"Invalid DHCP version: {dhcp_version}")
                return STATUS_NOK
            return STATUS_OK
        except Exception as e:
            self.log.error(f"Failed to add user context: {str(e)}")
            return STATUS_NOK
