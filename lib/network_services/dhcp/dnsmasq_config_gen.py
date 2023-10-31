class DnsmasqConfigurator:
    def __init__(self):
        self.config = []

    def add_listen_port(self, port):
        self.config.append(f'port={port}')

    def enable_domain_filtering(self):
        self.config.append('domain-needed')
        self.config.append('bogus-priv')

    def enable_dnssec(self, trust_anchors_conf_path=None):
        if trust_anchors_conf_path:
            self.config.append(f'conf-file={trust_anchors_conf_path}')
        self.config.append('dnssec')

    def enable_dnssec_check_unsigned(self):
        self.config.append('dnssec-check-unsigned')

    def enable_filter_windows_dns_requests(self):
        self.config.append('filterwin2k')

    def set_resolv_file(self, resolv_file_path):
        self.config.append(f'resolv-file={resolv_file_path}')

    def set_strict_order(self):
        self.config.append('strict-order')

    def disable_resolv_conf(self):
        self.config.append('no-resolv')

    def disable_poll_resolv_files(self):
        self.config.append('no-poll')

    def add_name_server(self, domain, ip_address):
        self.config.append(f'server=/{domain}/{ip_address}')

    def add_reverse_server(self, subnet, nameserver):
        self.config.append(f'server=/{subnet}.in-addr.arpa/{nameserver}')

    def add_local_only_domain(self, local_domain):
        self.config.append(f'local=/{local_domain}/')

    def force_domain_to_ip(self, domain, ip_address):
        self.config.append(f'address=/{domain}/{ip_address}')

    def add_ipv6_address(self, domain, ipv6_address):
        self.config.append(f'address=/{domain}/{ipv6_address}')

    def add_query_ips_to_ipset(self, domains, ipset_name):
        self.config.append(f'ipset=/{"/".join(domains)}/{ipset_name}')

    def add_query_ips_to_netfilter_sets(self, domains, sets):
        self.config.append(f'nftset=/{"/".join(domains)}/{",".join(sets)}')

    def add_ipv6_addresses_to_netfilter_sets(self, domains, sets):
        for domain in domains:
            for set in sets:
                self.config.append(f'nftset=/{domain}/{set}')

    def set_server_routing(self, ip_address, interface=None, source_address=None):
        server_setting = f'server={ip_address}'
        if interface:
            server_setting += f'@{interface}'
        if source_address:
            server_setting += f'@{source_address}'
        self.config.append(server_setting)

    def set_uid_and_gid(self, user=None, group=None):
        if user or group:
            user_group_setting = 'user=' + (user if user else '') + (',' if user and group else '') + (group if group else '')
            self.config.append(user_group_setting)

    def set_listen_interfaces(self, interfaces):
        for interface in interfaces:
            self.config.append(f'interface={interface}')

    def set_except_interfaces(self, interfaces):
        for interface in interfaces:
            self.config.append(f'except-interface={interface}')

    def set_listen_addresses(self, addresses):
        for address in addresses:
            self.config.append(f'listen-address={address}')

    def disable_dhcp_on_interface(self, interface):
        self.config.append(f'no-dhcp-interface={interface}')

    def bind_only_to_listened_interfaces(self):
        self.config.append('bind-interfaces')

    def disable_etc_hosts(self):
        self.config.append('no-hosts')

    def set_additional_hosts_file(self, hosts_file_path):
        self.config.append(f'addn-hosts={hosts_file_path}')

    def set_expand_hosts(self):
        self.config.append('expand-hosts')

    def set_domain(self, domain):
        self.config.append(f'domain={domain}')

    def set_domain_for_subnet(self, domain, subnet):
        self.config.append(f'domain={domain},{subnet}')

    def set_domain_for_range(self, domain, start_ip, end_ip):
        self.config.append(f'domain={domain},{start_ip},{end_ip}')

    def enable_dhcp_server(self, range_start, range_end, lease_time):
        self.config.append(f'dhcp-range={range_start},{range_end},{lease_time}')

    def enable_dhcp_server_with_netmask(self, range_start, range_end, netmask, lease_time):
        self.config.append(f'dhcp-range={range_start},{range_end},{netmask},{lease_time}')

    def enable_dhcp_server_with_tag(self, tag, range_start, range_end, lease_time):
        self.config.append(f'dhcp-range=set:{tag},{range_start},{range_end},{lease_time}')

    def enable_dhcp_server_for_tag(self, tag, range_start, range_end, lease_time):
        self.config.append(f'dhcp-range=set:tag,{range_start},{range_end},{lease_time}')

    def enable_tftp_server(self, root_directory):
        self.config.append(f'tftp-root={root_directory}')

    def set_boot_file(self, boot_file):
        self.config.append(f'pxe-service=x86PC,"{boot_file}"')

    def add_pxe_boot_option(self, option_number, option_value):
        self.config.append(f'pxe-service=x86PC,{option_number},{option_value}')

    def add_dhcp_option(self, option_number, option_value):
        self.config.append(f'dhcp-option={option_number},{option_value}')

    def set_dhcp_option_66(self, tftp_server):
        self.config.append(f'dhcp-option=66,{tftp_server}')

    def set_dhcp_option_67(self, boot_file):
        self.config.append(f'dhcp-option=67,{boot_file}')

    def set_dhcp_authoritative(self):
        self.config.append('dhcp-authoritative')

    def generate_configuration(self):
        return '\n'.join(self.config)
