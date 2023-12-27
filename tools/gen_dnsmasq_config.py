

from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSMasqConfigurator


configurator = DNSMasqConfigurator()

configurator.add_listen_port(53)
configurator.enable_domain_filtering()
configurator.enable_dnssec('/path/to/trust-anchors.conf')
configurator.enable_dnssec_check_unsigned()
configurator.enable_filter_windows_dns_requests()
configurator.set_resolv_file('/etc/resolv.conf')
configurator.set_strict_order()
configurator.disable_resolv_conf()
configurator.disable_poll_resolv_files()
configurator.add_name_server('example.com', '203.0.113.1')
configurator.add_reverse_server('192.168.0', '203.0.113.1')
configurator.add_local_only_domain('mylocaldomain')
configurator.force_domain_to_ip('example.net', '203.0.113.2')
configurator.add_ipv6_address('ipv6.example.com', '2001:db8::1')
configurator.add_query_ips_to_ipset(['example.org', 'sub.example.org'], 'myipset')
configurator.add_query_ips_to_netfilter_sets(['example.com', 'sub.example.com'], ['set1', 'set2'])
configurator.add_ipv6_addresses_to_netfilter_sets(['ipv6.example.com'], ['set3'])
configurator.set_server_routing('203.0.113.3')
configurator.set_uid_and_gid('dnsmasq', 'dnsmasq')
configurator.set_listen_interfaces(['eth0', 'eth1'])
configurator.set_except_interfaces(['eth2'])
configurator.set_listen_addresses(['192.168.0.1', '192.168.1.1'])
configurator.disable_dhcp_on_interface('eth0')
configurator.bind_only_to_listened_interfaces()
configurator.disable_etc_hosts()
configurator.set_additional_hosts_file('/etc/extra-hosts')
configurator.set_expand_hosts()
configurator.set_domain('example.local')
configurator.set_domain_for_subnet('example.net', '192.168.2.0')
configurator.set_domain_for_range('example.org', '192.168.3.1', '192.168.3.10')
configurator.add_dhcp4_range('192.168.0.100', '192.168.0.200', '12h')
configurator.add_dhcp4_range_with_netmask('192.168.1.50', '192.168.1.100', '255.255.255.0', '8h')
configurator.add_dhcp4_range_with_tag('mytag', '192.168.2.10', '192.168.2.20', '6h')
configurator.add_dhcp4_range_with_tag('mytag', '192.168.2.10', '192.168.2.20', '6h')
configurator.set_tftp_server('/path/to/tftp')
configurator.set_boot_file('pxelinux.0')
configurator.add_pxe_boot_option(150, 'pxelinux.0')
configurator.add_dhcp_option(66, '203.0.113.4')
configurator.add_dhcp_option(67, 'bootfile')
configurator.set_dhcp_authoritative()

# Generate the dnsmasq configuration
dnsmasq_configuration = configurator.generate_configuration()

# You can write the generated configuration to a file or use it as needed
with open('/etc/dnsmasq.conf', 'w') as config_file:
    config_file.write(dnsmasq_configuration)