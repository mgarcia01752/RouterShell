#!/usr/bin/env python3


from lib.cli.show.router_configuration import RouterConfiguration
from lib.db.router_config_db import RouterConfigurationDatabase
from lib.network_manager.interface import Interface
from lib.network_manager.network_manager import InterfaceType


print(Interface().get_interface_info('enx00249b119cef')['businfo'])

    



