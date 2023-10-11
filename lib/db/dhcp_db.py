import copy
import ipaddress
import json
from typing import Dict, Union

class DHCPDatabase:
    """
    DHCPDatabase class for managing DHCP configuration.
    """

    dhcp_pool = {
        "DhcpPool": {
            "pool-name": [
                {
                    "subnet-id": "",
                    "name": ""
                }
            ]
        }
    }

    kea_dhcpv4_config = {
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

    def __init__(self, config_file: str = None):
        """
        Initialize the DHCPDatabase instance.

        Args:
            config_file (str, optional): The path to the DHCP configuration file.
        """
        self.config_file = config_file

    def add_subnet(self, subnet_id: int, subnet_range: str, client_class: str, relay_ip: str):
        """
        Add a subnet to the DHCP configuration.

        Args:
            subnet_id (int): The unique ID of the subnet.
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
        self.kea_dhcpv4_config["Dhcp4"]["subnet4"].append(new_subnet)

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
        for subnet in self.kea_dhcpv4_config["Dhcp4"]["subnet4"]:
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
        for subnet in self.kea_dhcpv4_config["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                # Create a new pool configuration
                new_pool = {
                    "pool": f"{ip_pool_start} - {ip_pool_end}",
                    "reservations": []
                }
                # Append the new pool to the subnet's pools list
                subnet["pools"].append(new_pool)
                break  # Exit the loop once the subnet is found

    def add_pool_name(self, pool_name: str, subnet_id: str) -> bool:
        """
        Add a pool name to the DHCP configuration and associate it with a subnet ID.

        Args:
            pool_name (str): The name of the pool to add.
            subnet_id (str): The ID of the subnet to associate the pool with.

        Returns:
            bool: True if the pool name was added successfully, False if it already exists.
        """
        # Check if the pool name already exists
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return False  # Pool name already exists

        # If the pool name doesn't exist, add it
        new_pool_entry = {
            "subnet-id": subnet_id,
            "name": pool_name
        }
        self.dhcp_pool["DhcpPool"]["pool-name"].append(new_pool_entry)
        return True  # Pool name added successfully

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
        dhcp_config = self.kea_dhcpv4_config if dhcp_version == 0 else self.kea_dhcpv6_config

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
            json.dump(self.kea_dhcpv4_config, file, indent=4)

    def get_dhcp_pool(self) -> Dict:
        """
        Get a deep copy of the DHCP pool configuration.

        Returns:
            dict: A deep copy of the DHCP pool configuration.
        """
        return copy.deepcopy(self.dhcp_pool)

    def get_kea_dhcpv4_config(self) -> Dict:
        """
        Get a deep copy of the KEA DHCPv4 configuration.

        Returns:
            dict: A deep copy of the KEA DHCPv4 configuration.
        """
        return copy.deepcopy(self.kea_dhcpv4_config)

class DhcpOptionsLUT:
    '''https://kea.readthedocs.io/en/latest/arm/dhcp4-srv.html#interface-configuration'''
    
    def __init__(self):
        
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

