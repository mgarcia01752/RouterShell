#!/usr/bin/env python3


from lib.cli.show.router_configuration import RouterConfiguration
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.network_manager.network_manager import InterfaceType


rcdb = RouterConfigurationDatabase()

print(rcdb.get_dhcp_server_configuration())
    

