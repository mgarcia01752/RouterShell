#!/usr/bin/env python3


from lib.cli.show.router_configuration import RouterConfiguration
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.network_manager.network_manager import InterfaceType


rcdb = RouterConfigurationDatabase()

ifName_list = rcdb.get_interface_name_list(InterfaceType.ETHERNET)

for ifName in ifName_list:
    print(f'Interface: {ifName}')
    
    status, ifName_config = rcdb.get_interface_configuration(ifName)
    
    if status:
        print(f"ERROR - Unable to get config for interface: {ifName}")
        
    print(ifName_config)

print("\n\n\n\n")

rc = RouterConfiguration()

run_config = rc.get_running_configuration()
for line in run_config:
    print(line)
    

