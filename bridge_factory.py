#!/usr/bin/env python3

import logging
from lib.network_manager.common.phy import State
from lib.network_manager.network_operations.bridge.bridge import Bridge
from lib.network_manager.network_operations.bridge.bridge_factory import BridgeConfigFactory
from lib.network_manager.network_operations.bridge.bridge_settings import STP_STATE

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

if Bridge()._del_bridge_via_os(bridge_name):
    logging.info(f"Bridge {bridge_name} failed to deleted")

# Initialize BridgeConfigFactory and get BridgeConfigCommands
bcc = BridgeConfigFactory(bridge_name=bridge_name).get_bridge_config_cmds()

# Check if bridge exists
print(f"Checking if bridge {bridge_name} exists")
if not bcc.does_bridge_exist():
    print(f"Bridge {bridge_name} does not exist. Creating bridge.")
    if bcc.create_bridge():
        print(f"Failed to creae Bridge {bridge_name}")
        exit()
    print(f'Created bridge {bridge_name}')
    
else:
    print(f"Bridge {bridge_name} already exists.")

input("Press Enter to continue...")

# Set description
print(f"Setting description to: {description}")
if bcc.set_description(description):
    print(f'Failed to add description: {description}')
    exit()

input("Press Enter to continue...")

# Set management IP address
print(f"Setting management IP address to: {mgt_inet}")
if bcc.set_inet_management(mgt_inet):
    print(f'Failed to add mgt-inet: {mgt_inet}')
    exit()

input("Press Enter to continue...")

# Enable STP
print("Enabling STP")
if bcc.set_stp(stp=STP_STATE.STP_ENABLE):
    print(f'Failed to add STP {STP_STATE.STP_ENABLE}')
    exit()
    
input("Press Enter to continue...")

# Set bridge to no shutdown
print("Setting bridge to no shutdown")
if bcc.set_shutdown_status(state=State.UP):
    print(f'Failed to no shutdown')
    exit()

input("Press Enter to continue...")

# Disable STP
print("Disabling STP")
bcc.set_stp(stp=STP_STATE.STP_DISABLE)
input("Press Enter to continue...")

# Set bridge to shutdown
print("Setting bridge to shutdown")
bcc.set_shutdown_status(state=State.DOWN)
input("Press Enter to continue...")

print("Manual test completed.")
