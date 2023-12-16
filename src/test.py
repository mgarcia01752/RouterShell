#!/usr/bin/env python3

import json

from lib.network_manager.dhcp_server import DhcpServerManager

def main():
    # Create an instance of DhcpServerManager
    dhcp_manager = DhcpServerManager()

    # Get DHCP lease summary
    dhcp_lease_summary = dhcp_manager.get_leases()

    # Display the DHCP lease summary
    print("DHCP Lease Summary:")
    print(json.dumps(dhcp_lease_summary, indent=2))

if __name__ == "__main__":
    main()



    



