import copy
from enum import Enum
import ipaddress
import json
import logging
from typing import Dict, Union


from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_services.dhcp.common.dhcp_common import DHCPVersion

class DhcpVersion(Enum):
    """An enumeration of DHCP versions: DHCPv4 and DHCPv6."""
    DHCP_V4 = 'DHCPv4'
    DHCP_V6 = 'DHCPv6'

class KeaDHCPDBFactory():
    def __init__(self, dhcp_pool_name: str, ip_subnet_mask: str, negate=False):
        self.log = logging.getLogger(self.__class__.__name__)

        try:
            # Attempt to create an IPv4Network or IPv6Network object from the provided subnet string
            self.ip_subnet_mask = ipaddress.ip_network(ip_subnet_mask, strict=False)
            self.log.debug(f"Subnet: {self.ip_subnet_mask}")
        except ValueError:
            self.log.error("Invalid subnet format. Please provide a valid subnet in CIDR notation.")
            raise ValueError("Invalid subnet format. Please provide a valid subnet in CIDR notation.")

        self.dhcp_pool_name = dhcp_pool_name
        self.negate = negate

        self.kea_db_obj = KeaDHCPDB()
       
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

    def add_pool_name(self, id: int, pool_name: str, dhcp_version: DHCPVersion) -> bool:
        """
        Add a pool name to the database.

        Args:
            id (int): The ID of the pool.
            pool_name (str): The name of the pool.
            dhcp_version (DhcpVersion): The DHCP version (DhcpVersion.DHCP_V4 or DhcpVersion.DHCP_V6).

        Returns:
            bool: STATUS_OK if the pool name was added, STATUS_NOK otherwise.
        """
        self.log.debug(f"add_pool_name() -> {pool_name} -> DHCP-Version: {dhcp_version}")
        
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
        self.log.debug(f"get_num_of_subnets() -> {dhcp_version}")
        
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
        self.log.debug(f"set_subnet() -> {ip_subnet} -> {dhcp_version}")
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