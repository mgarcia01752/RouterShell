#!/usr/bin/env python3

import logging
from lib.network_manager.common.phy import State
from lib.network_manager.network_operations.bridge.bridge_factory import BridgeConfigFactory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/log/routershell.log')
    ]
)

bridge_name = "brlan0"
mgt_inet = "10.10.10.1"
description = f"Test Bridge: {bridge_name}"

# Initialize BridgeConfigFactory and get BridgeConfigCommands
bcc = BridgeConfigFactory(bridge_name=bridge_name).get_bridge_config_cmds()

# Check if bridge exists
print(f"Checking if bridge {bridge_name} exists")
if not bcc.does_bridge_exist():
    print(f"Bridge {bridge_name} does not exist. Creating bridge.")
    if bcc.create_bridge():
        print(f"Failed to creae Bridge {bridge_name}")
else:
    print(f"Bridge {bridge_name} already exists.")

# Set description
print(f"Setting description to: {description}")
bcc.set_description(description)
input("Press Enter to continue...")

# Set management IP address
print(f"Setting management IP address to: {mgt_inet}")
bcc.set_inet_management(mgt_inet)
input("Press Enter to continue...")

# Enable STP
print("Enabling STP")
bcc.set_stp(stp=State.STP_ENABLE)
input("Press Enter to continue...")

# Set bridge to no shutdown
print("Setting bridge to no shutdown")
bcc.set_shutdown_status(shutdown_state=State.UP)
input("Press Enter to continue...")

# Disable STP
print("Disabling STP")
bcc.set_stp(stp=State.STP_DISABLE)
input("Press Enter to continue...")

# Set bridge to shutdown
print("Setting bridge to shutdown")
bcc.set_shutdown_status(shutdown_state=State.DOWN)
input("Press Enter to continue...")

print("Manual test completed.")
