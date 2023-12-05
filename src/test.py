#!/usr/bin/env python3


from lib.cli.show.router_configuration import RouterConfiguration
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.network_manager.network_manager import InterfaceType

print("\n")
print("; RouterShell Running-Configuration")
print("\n")

rc = RouterConfiguration()

run_config = rc.get_running_configuration()
for line in run_config:
    print(line)
    

