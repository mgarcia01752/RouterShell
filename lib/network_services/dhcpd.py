import ipaddress
import logging


from lib.db.dhcpd_db import DHCPDatabase
from lib.common.common import STATUS_NOK, STATUS_OK

class DHCPServer():

    def __init__(self):
        self.is_running = False
        
    def configure_interface(self, 
                            interface: str,
                            dhcp_pool_name:str, 
                            subnet: ipaddress,
                            subnet_mask: ipaddress, 
                            range_start: ipaddress, 
                            range_end: ipaddress, 
                            router: ipaddress, 
                            dns_servers: list[str]):
        """
        Configure DHCP parameters for an interface.

        Args:
            interface (str): The name of the network interface.
            subnet (str): The subnet in CIDR notation (e.g., '192.168.1.0/24').
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            router (str): The IP address of the default gateway (router).
            dns_servers (List[str]): A list of DNS server IP addresses.

        Linux Execution:
        
        subnet 192.168.1.0 netmask 255.255.255.0 {
            range 192.168.1.10 192.168.1.50;
            option subnet-mask 255.255.255.0;
            option routers 192.168.1.1; # Your NAT router's IP
            option domain-name-servers 8.8.8.8, 8.8.4.4; # DNS servers
            option domain-name "example.com";
        }
        
        """
    pass

    def start_server(self):
        """
        Start the DHCP servers for all configured interfaces.
        """
        if not self.is_running:
            for interface, config in self.interfaces.items():
                subnet = config['subnet']
                range_start, range_end = config['range']
                router = config['router']
                dns_servers = config['dns_servers']

                # Execute a DHCP server process (replace with your DHCP server command)
                cmd = f"dhcpd -cf /etc/dhcp/dhcpd-{interface}.conf {interface}"
                subprocess.Popen(cmd, shell=True)

            self.is_running = True
        else:
            print("DHCP server is already running.")

    def stop_server(self):
        """
        Stop all running DHCP servers.
        """
        if self.is_running:
            # Terminate all DHCP server processes (replace with your termination logic)
            subprocess.run(["pkill", "dhcpd"])

            self.is_running = False
        else:
            print("DHCP server is not running.")

    def reset_server(self):
        """
        Reset the DHCP server configuration.
        """
        self.stop_server()
        self.interfaces = {}

    def update_interface(self, interface, new_config):
        pass
        
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

    def verify_key_exists(self, key):
        return key in self.options

    def get_data_type(self, key):
        if self.verify_key_exists(key):
            return self.options[key]
        else:
            return None
