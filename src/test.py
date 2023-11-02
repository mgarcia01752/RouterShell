#!/usr/bin/env python3

from lib.network_services.dhcp.dnsmasq.dnsmasq import DNSMasqInterfaceService 

pool = 'dhcp-home-office-1'
subnet = '172.16.1.0/24'

dmis = DNSMasqInterfaceService(pool, subnet)

dmis.build_interface_configuration()