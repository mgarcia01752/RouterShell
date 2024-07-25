#!/usr/bin/env python3

from lib.network_manager.network_operations.dhcp.client.supported_dhcp_clients import DHCPClientFactory
obj = DHCPClientFactory().get_supported_dhcp_client('eno1')
print(obj.get_dhcp_client())


