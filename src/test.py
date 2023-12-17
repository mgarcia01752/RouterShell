#!/usr/bin/env python3

import json
from lib.cli.show.router_configuration import RouterConfiguration

from lib.db.router_config_db import RouterConfigurationDatabase

RouterConfigurationDatabase().get_wifi_policy_configuration()

wifi_policy_config = RouterConfiguration()._get_global_wifi_policy()

print("###########################MAIN###########################")
for line in wifi_policy_config:
    print(line)
    



