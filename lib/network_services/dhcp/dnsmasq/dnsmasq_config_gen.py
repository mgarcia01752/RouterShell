from enum import Enum
import logging
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_OK, STATUS_NOK
from typing import List, Union

class DHCPv6Modes(Enum):

    '''
        For IPv6, the mode may be some combination of ra-only, slaac, ra-names, ra-stateless, ra-advrouter, off-link.

        - `ra-only` tells dnsmasq to offer Router Advertisement only on this subnet, and not DHCP.

        - `slaac` tells dnsmasq to offer Router Advertisement on this subnet and to set the A bit in the router advertisement, so that the client will use SLAAC addresses. When used with a DHCP range or static DHCP address this results in the client having both a DHCP-assigned and a SLAAC address.

        - `ra-stateless` sends router advertisements with the O and A bits set, and provides a stateless DHCP service. The client will use a SLAAC address, and use DHCP for other configuration information.

        - `ra-names` enables a mode which gives DNS names to dual-stack hosts which do SLAAC for IPv6. Dnsmasq uses the host's IPv4 lease to derive the name, network segment and MAC address and assumes that the host will also have an IPv6 address calculated using the SLAAC algorithm, on the same network segment. The address is pinged, and if a reply is received, an AAAA record is added to the DNS for this IPv6 address. Note that this is only happens for directly-connected networks, (not one doing DHCP via a relay) and it will not work if a host is using privacy extensions. ra-names can be combined with ra-stateless and slaac.

        - `ra-advrouter` enables a mode where router address(es) rather than prefix(es) are included in the advertisements. This is described in RFC-3775 section 7.2 and is used in mobile IPv6. In this mode the interval option is also included, as described in RFC-3775 section 7.3.

        - `off-link` tells dnsmasq to advertise the prefix without the on-link (aka L) bit set.    
    '''
    
    RA_ONLY = 'ra-only'
    RA_NAMES = 'ra-names'
    RA_STATELESS = 'ra-stateless'
    RA_ADV_ROUTER = 'ra-advrouter'
    SLAAC = 'slaac'
    OFF_LINK = 'off-link'

    @classmethod
    def get_key(cls, value):
        """Get the key for a given value in the enum."""
        for key, member in cls.__members__.items():
            if member.value == value:
                return key
            
        raise ValueError(f"No key found for value '{value}' in DHCPv6Modes enum.")
    
    @classmethod
    def get_mode(cls, value):
        """Get the enum member for a given value in the enum."""
        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"No mode found for value '{value}' in DHCPv6Modes enum.")


class DNSMasqConfigurator:
    '''
    For the latest DNSmasq configuration:
    https://thekelleys.org.uk/dnsmasq/docs/dnsmasq.conf.example
    
    https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
    
    '''
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_CONFIG)        
        self.config = []

    def add_listen_port(self, port: int):
        '''
        Add a listen port to the DNSMasq configuration.

        Args:
            port (int): The port number to listen on.
        '''
        self.config.append(f'port={port}')

    def enable_domain_filtering(self):
        '''
        Enable domain filtering in the DNSMasq configuration.
        '''
        self.config.append('domain-needed')
        self.config.append('bogus-priv')

    def enable_dnssec(self, trust_anchors_conf_path: str = None):
        '''
        Enable DNSSEC in the DNSMasq configuration.

        Args:
            trust_anchors_conf_path (str, optional): Path to a trust anchors configuration file.
        '''
        if trust_anchors_conf_path:
            self.config.append(f'conf-file={trust_anchors_conf_path}')
        self.config.append('dnssec')

    def enable_dnssec_check_unsigned(self):
        '''
        Enable DNSSEC check for unsigned domains in the DNSMasq configuration.
        '''
        self.config.append('dnssec-check-unsigned')

    def enable_filter_windows_dns_requests(self):
        '''
        Enable filtering of Windows DNS requests in the DNSMasq configuration.
        '''
        self.config.append('filterwin2k')

    def set_resolv_file(self, resolv_file_path: str):
        '''
        Set the resolv file path in the DNSMasq configuration.

        Args:
            resolv_file_path (str): Path to the resolv file.
        '''
        self.config.append(f'resolv-file={resolv_file_path}')

    def set_strict_order(self):
        '''
        Set strict DNS server order in the DNSMasq configuration.
        '''
        self.config.append('strict-order')

    def disable_resolv_conf(self):
        '''
        Disable using the resolv.conf file in the DNSMasq configuration.
        '''
        self.config.append('no-resolv')

    def disable_poll_resolv_files(self):
        '''
        Disable polling resolv files in the DNSMasq configuration.
        '''
        self.config.append('no-poll')

    def add_name_server(self, domain: str, ip_address: str):
        '''
        Add a name server to the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the IP address.
            ip_address (str): The IP address of the name server.
        '''
        self.config.append(f'server=/{domain}/{ip_address}')

    def add_reverse_server(self, subnet: str, nameserver: str):
        '''
        Add a reverse DNS server to the DNSMasq configuration.

        Args:
            subnet (str): The subnet to associate with the nameserver.
            nameserver (str): The IP address of the nameserver.
        '''
        self.config.append(f'server=/{subnet}.in-addr.arpa/{nameserver}')

    def add_local_only_domain(self, local_domain: str):
        '''
        Add a local-only domain to the DNSMasq configuration.

        Args:
            local_domain (str): The local domain to add.
        '''
        self.config.append(f'local=/{local_domain}/')

    def force_domain_to_ip(self, domain: str, ip_address: str):
        '''
        Force a domain to resolve to a specific IP address in the DNSMasq configuration.

        Args:
            domain (str): The domain to force to the IP address.
            ip_address (str): The IP address to resolve the domain to.
        '''
        self.config.append(f'address=/{domain}/{ip_address}')

    def add_ipv6_address(self, domain: str, ipv6_address: str):
        '''
        Add an IPv6 address for a domain in the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the IPv6 address.
            ipv6_address (str): The IPv6 address of the domain.
        '''
        self.config.append(f'address=/{domain}/{ipv6_address}')

    def add_query_ips_to_ipset(self, domains: List[str], ipset_name: str):
        '''
        Add query IPs to an IPset in the DNSMasq configuration.

        Args:
            domains (List[str]): List of domains to associate with the IPset.
            ipset_name (str): Name of the IPset.
        '''
        self.config.append(f'ipset=/{"/".join(domains)}/{ipset_name}')

    def add_query_ips_to_netfilter_sets(self, domains: List[str], sets: List[str]):
        '''
        Add query IPs to netfilter sets in the DNSMasq configuration.

        Args:
            domains (List[str]): List of domains to associate with netfilter sets.
            sets (List[str]): List of netfilter sets to add the domains to.
        '''
        self.config.append(f'nftset=/{"/".join(domains)}/{",".join(sets)}')

    def add_ipv6_addresses_to_netfilter_sets(self, domains: List[str], sets: List[str]):
        '''
        Add IPv6 addresses to netfilter sets in the DNSMasq configuration.

        Args:
            domains (List[str]): List of domains to associate with netfilter sets.
            sets (List[str]): List of netfilter sets to add the domains to.
        '''
        for domain in domains:
            for set in sets:
                self.config.append(f'nftset=/{domain}/{set}')

    def set_server_routing(self, ip_address: str, interface: str = None, source_address: str = None):
        '''
        Set server routing in the DNSMasq configuration.

        Args:
            ip_address (str): The IP address of the server.
            interface (str, optional): The network interface to bind to.
            source_address (str, optional): The source IP address to use.
        '''
        server_setting = f'server={ip_address}'
        if interface:
            server_setting += f'@{interface}'
        if source_address:
            server_setting += f'@{source_address}'
        self.config.append(server_setting)

    def set_uid_and_gid(self, user: str = None, group: str = None):
        '''
        Set the user and group for DNSMasq in the configuration.

        Args:
            user (str, optional): The user to run DNSMasq as.
            group (str, optional): The group to run DNSMasq as.
        '''
        if user or group:
            user_group_setting = 'user=' + \
                (user if user else '') + \
                (',' if user and group else '') + (group if group else '')
            self.config.append(user_group_setting)

    def set_listen_interfaces(self, interfaces: List[str]):
        '''
        Set listen interfaces for DNSMasq in the configuration.

        Args:
            interfaces (List[str]): List of network interfaces to listen on.
        '''
        for interface in interfaces:
            self.config.append(f'interface={interface}')

    def set_except_interfaces(self, interfaces: List[str]):
        '''
        Set exceptions for network interfaces in the DNSMasq configuration.

        Args:
            interfaces (List[str]): List of network interfaces to exclude.
        '''
        for interface in interfaces:
            self.config.append(f'except-interface={interface}')

    def set_listen_addresses(self, addresses: List[str]):
        '''
        Set listen addresses for DNSMasq in the configuration.

        Args:
            addresses (List[str]): List of IP addresses to listen on.
        '''
        for address in addresses:
            self.config.append(f'listen-address={address}')

    def disable_dhcp_on_interface(self, interface: str):
        '''
        Disable DHCP on a specific network interface in the DNSMasq configuration.

        Args:
            interface (str): The network interface to disable DHCP on.
        '''
        self.config.append(f'no-dhcp-interface={interface}')

    def bind_only_to_listened_interfaces(self):
        '''
        Enable binding only to listened interfaces in the DNSMasq configuration.
        '''
        self.config.append('bind-interfaces')

    def disable_etc_hosts(self):
        '''
        Disable using the /etc/hosts file in the DNSMasq configuration.
        '''
        self.config.append('no-hosts')

    def set_additional_hosts_file(self, hosts_file_path: str):
        '''
        Set an additional hosts file in the DNSMasq configuration.

        Args:
            hosts_file_path (str): Path to an additional hosts file.
        '''
        self.config.append(f'addn-hosts={hosts_file_path}')

    def set_expand_hosts(self):
        '''
        Enable expanding hosts in the DNSMasq configuration.
        '''
        self.config.append('expand-hosts')

    def set_domain(self, domain: str):
        '''
        Set the domain in the DNSMasq configuration.

        Args:
            domain (str): The domain to set.
        '''
        self.config.append(f'domain={domain}')

    def set_domain_for_subnet(self, domain: str, subnet: str):
        '''
        Set a domain for a subnet in the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the subnet.
            subnet (str): The subnet to set the domain for.
        '''
        self.config.append(f'domain={domain},{subnet}')

    def set_domain_for_range(self, domain: str, start_ip: str, end_ip: str):
        '''
        Set a domain for an IP range in the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the IP range.
            start_ip (str): The start IP address of the range.
            end_ip (str): The end IP address of the range.
        '''
        self.config.append(f'domain={domain},{start_ip},{end_ip}')

    def add_dhcp4_range(self, range_start: str, range_end: str, lease_time: int):
        '''
        Add a DHCP server range in the DNSMasq configuration for IPv4.

        Args:
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            lease_time (int): The lease time for DHCP leases.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{lease_time}')

    def add_dhcp4_range_with_netmask(self, range_start: str, range_end: str, netmask: str, lease_time: int):
        '''
        Add a DHCP server range with netmask in the DNSMasq configuration for IPv4.

        Args:
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            netmask (str): The netmask for the DHCP range.
            lease_time (int): The lease time for DHCP leases.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{netmask},{lease_time}')

    def add_dhcp4_range_with_tag(self, tag: str, range_start: str, range_end: str, lease_time: int):
        '''
        Add a DHCP server range with a tag in the DNSMasq configuration for IPv4.

        Args:
            tag (str): The tag to associate with the DHCP range.
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            lease_time (int): The lease time for DHCP leases.
        '''
        self.config.append(
            f'dhcp-range=set:{tag},{range_start},{range_end},{lease_time}')

    def add_dhcp6_range(self, range_start: str, range_end: str, lease_time: int, mode: DHCPv6Modes):
        '''
        Add a DHCPv6 server range in the DNSMasq configuration.

        Args:
            range_start (str): The start IPv6 address of the DHCPv6 range.
            range_end (str): The end IPv6 address of the DHCPv6 range.
            lease_time (int): The lease time for DHCPv6 leases.
            mode (DHCPv6Modes): The DHCPv6 mode to configure.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{lease_time},constructor:{self.interface},{mode.value}')

    def add_dhcp6_range_with_prefix_len(self, range_start: str, range_end: str, prefix_len: int, lease_time: int, mode: DHCPv6Modes):
        '''
        Add a DHCPv6 server range with prefix length in the DNSMasq configuration.

        Args:
            range_start (str): The start IPv6 address of the DHCPv6 range.
            range_end (str): The end IPv6 address of the DHCPv6 range.
            prefix_len (int): The prefix length for the DHCPv6 range.
            lease_time (int): The lease time for DHCPv6 leases.
            mode (DHCPv6Modes): The DHCPv6 mode to configure.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{mode.value},{prefix_len},{lease_time}')

    def add_dhcp6_range_with_tag(self, tag: str, range_start: str, range_end: str, lease_time: int, mode: DHCPv6Modes):
        '''
        Add a DHCPv6 server range with a tag in the DNSMasq configuration.

        Args:
            tag (str): The tag to associate with the DHCPv6 range.
            range_start (str): The start IPv6 address of the DHCPv6 range.
            range_end (str): The end IPv6 address of the DHCPv6 range.
            lease_time (int): The lease time for DHCPv6 leases.
            mode (DHCPv6Modes): The DHCPv6 mode to configure.
        '''
        self.config.append(
            f'dhcp-range=set:{tag},{range_start},{range_end},{lease_time},constructor:{self.interface},{mode.value}')

    def set_tftp_server(self, root_directory: str):
        '''
        Set a TFTP server in the DNSMasq configuration.

        Args:
            root_directory (str): The root directory for TFTP.
        '''
        self.config.append(f'tftp-root={root_directory}')

    def set_boot_file(self, boot_file: str):
        '''
        Set the boot file in the DNSMasq configuration.

        Args:
            boot_file (str): The boot file to set.
        '''
        self.config.append(f'pxe-service=x86PC,"{boot_file}"')

    def add_pxe_boot_option(self, option_number: int, option_value: str):
        '''
        Add a PXE boot option in the DNSMasq configuration.

        Args:
            option_number (int): The PXE option number.
            option_value (str): The value of the PXE option.
        '''
        self.config.append(f'pxe-service=x86PC,{option_number},{option_value}')

    def add_dhcp_option(self, option_number: int, option_value: str):
        '''
        Add a DHCP option in the DNSMasq configuration.

        Args:
            option_number (int): The DHCP option number.
            option_value (str): The value of the DHCP option.
        '''
        self.config.append(f'dhcp-option={option_number},{option_value}')

    def set_dhcp_option_66(self, tftp_server: str):
        '''
        Set DHCP option 66 (TFTP server) in the DNSMasq configuration.

        Args:
            tftp_server (str): The TFTP server address.
        '''
        self.config.append(f'dhcp-option=66,{tftp_server}')

    def set_dhcp_option_67(self, boot_file: str):
        '''
        Set DHCP option 67 (Boot file) in the DNSMasq configuration.

        Args:
            boot_file (str): The boot file path.
        '''
        self.config.append(f'dhcp-option=67,{boot_file}')

    def set_dhcp_authoritative(self):
        """
        Set the DHCP server as authoritative in the configuration.
        """
        self.config.append('dhcp-authoritative')

    def add_dhcp_host(self, *args: Union[str, int]):
        '''
        Add a DHCP host configuration to the DNSMasq configuration.

        Args:
            *args (Union[str, int]): Variable number of arguments.
                - If only one argument is provided, it is assumed to be the Ethernet address.
                - If two arguments are provided, the first is assumed to be the Ethernet address, and the second is the IP address.
                - If three arguments are provided, the first is the Ethernet address, the second is the name, and the third is the IP address.
                - If four arguments are provided, the first is the Ethernet address, the second is the name, the third is the IP address, and the fourth is the lease time.

        Examples:
            - add_dhcp_host("11:22:33:44:55:66", "192.168.0.60")
            - add_dhcp_host("11:22:33:44:55:66", "fred")
            - add_dhcp_host("11:22:33:44:55:66", "fred", "192.168.0.60")
            - add_dhcp_host("11:22:33:44:55:66", "fred", "192.168.0.60", "45m")
        '''
        if len(args) == 1:
            self.config.append(f'dhcp-host={args[0]}')
        elif len(args) == 2:
            self.config.append(f'dhcp-host={args[0]},{args[1]}')
        elif len(args) == 3:
            self.config.append(f'dhcp-host={args[0]},{args[1]},{args[2]}')
        elif len(args) == 4:
            self.config.append(f'dhcp-host={args[0]},{args[1]},{args[2]},{args[3]}')

    def add_dhcp_host_with_client_id(self, client_id: str, ip_address: str):
        '''
        Add a DHCP host configuration with a client identifier to the DNSMasq configuration.

        Args:
            client_id (str): The client identifier.
            ip_address (str): The IP address.

        Example:
            add_dhcp_host_with_client_id("01:02:02:04", "192.168.0.60")
        '''
        self.config.append(f'dhcp-host=id:{client_id},{ip_address}')

    def add_dhcp_host_with_infiniband(self, hardware_address: str, ip_address: str):
        '''
        Add a DHCP host configuration with InfiniBand hardware address to the DNSMasq configuration.

        Args:
            hardware_address (str): The InfiniBand hardware address.
            ip_address (str): The IP address.

        Example:
            add_dhcp_host_with_infiniband("ff:00:00:00:00:00:02:00:00:02:c9:00:f4:52:14:03:00:28:05:81", "192.168.0.61")
        '''
        self.config.append(f'dhcp-host=id:{hardware_address},{ip_address}')

    def add_dhcp_host_with_name(self, client_name: str, ip_address: str, lease_time: str):
        '''
        Add a DHCP host configuration with a client name, IP address, and lease time to the DNSMasq configuration.

        Args:
            client_name (str): The client name.
            ip_address (str): The IP address.
            lease_time (str): The lease time.

        Example:
            add_dhcp_host_with_name("bert", "192.168.0.70", "infinite")
        '''
        self.config.append(f'dhcp-host={client_name},{ip_address},{lease_time}')

    def enable_dhcp_host_ignore(self, ethernet_address: str):
        '''
        Enable ignoring DHCP requests from a specific host with the given Ethernet address.

        Args:
            ethernet_address (str): The Ethernet address to ignore.

        Example:
            enable_dhcp_host_ignore("11:22:33:44:55:66")
        '''
        self.config.append(f'dhcp-host={ethernet_address},ignore')

    def enable_dhcp_host_ignore_client_id(self, ethernet_address: str):
        '''
        Enable ignoring DHCP client ID presented by a host with the given Ethernet address.

        Args:
            ethernet_address (str): The Ethernet address.

        Example:
            enable_dhcp_host_ignore_client_id("11:22:33:44:55:66")
        '''
        self.config.append(f'dhcp-host={ethernet_address},id:*')

    def enable_dhcp_host_set_extra_options(self, ethernet_address: str, options_tag: str):
        '''
        Send extra options tagged with a specific identifier to a host with the given Ethernet address.

        Args:
            ethernet_address (str): The Ethernet address.
            options_tag (str): The options tag.

        Example:
            enable_dhcp_host_set_extra_options("11:22:33:44:55:66", "set:red")
        '''
        self.config.append(f'dhcp-host={ethernet_address},{options_tag}')

    def enable_dhcp_host_set_extra_options_pattern(self, ethernet_pattern: str, options_tag: str):
        '''
        Send extra options tagged with a specific identifier to any host with Ethernet addresses matching a pattern.

        Args:
            ethernet_pattern (str): The Ethernet address pattern.
            options_tag (str): The options tag.

        Example:
            enable_dhcp_host_set_extra_options_pattern("11:22:33:*:*:*", "set:red")
        '''
        self.config.append(f'dhcp-host={ethernet_pattern},{options_tag}')

    def generate_configuration(self):
        """
        Generate the DNSMasq configuration as a string.

        Returns:
            str: The DNSMasq configuration as a string.
        """
        return '\n'.join(self.config)
