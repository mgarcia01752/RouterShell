#!/usr/bin/env python3

from lib.network_services.dhcp.dnsmasq.dnsmasq import Action, DNSMasqInterfaceService, DNSMasqDeploy 

pool = 'dhcp-home-office-1'
subnet = '172.16.1.0/24'

dmis = DNSMasqInterfaceService(pool, subnet)
dmis.build_interface_configuration()
dmis.deploy_configuration(DNSMasqDeploy.INTERFACE)


pool = 'dhcp-home-office-2'
subnet = '172.16.2.0/24'
dmis2 = DNSMasqInterfaceService(pool, subnet)
dmis2.build_interface_configuration()
dmis2.deploy_configuration(DNSMasqDeploy.INTERFACE)


pool = 'dhcp-home-office-3'
subnet = '172.16.3.0/24'
dmis3 = DNSMasqInterfaceService(pool, subnet)
dmis3.build_interface_configuration()
dmis3.deploy_configuration(DNSMasqDeploy.INTERFACE)

dmis3.control_service(Action.RESTART)

