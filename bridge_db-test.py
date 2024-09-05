#!/usr/bin/env python3

from lib.db.sqlite_db.router_shell_db import RouterShellDB
from lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE, BridgeProtocol


bridge_name = "brlan0"
description = "Test Bridge Insert"
protocol = BridgeProtocol.IEEE_802_1D
stp_status = STP_STATE.STP_ENABLE
management_inet = '192.168.200.1'
shutdown_status = True
interface_name='eno1'

# Initialize RouterShellDB
db = RouterShellDB()

# Insert a new bridge
print(f"Inserting bridge: {bridge_name}")
insert_result = db.insert_interface_bridge(bridge_name, shutdown_status)
print(f"Insert result: {insert_result}")

# If insertion was successful, delete the bridge
if insert_result.status:
    print(f"Deleting bridge: {bridge_name}")
    delete_result = db.delete_interface_bridge(bridge_name)
    print(f"Delete result: {delete_result}")

# Pause to check the database
input("Press Enter to continue to the next step...")

# Update the bridge
print(f"Updating bridge: {bridge_name}")
update_result = db.update_bridge(
    bridge_name=bridge_name,
    protocol=protocol,
    stp_status=stp_status,
    management_inet=management_inet,
    description=description,
    shutdown_status=shutdown_status
)
print(f"Update result: {update_result}")

# Pause to check the database
input("Press Enter to continue to the next step...")

print('Adding Bridge {} to Interface')


# Delete the bridge
print(f"Deleting bridge: {bridge_name}")
delete_result = db.delete_interface_bridge(bridge_name)
print(f"Delete result: {delete_result}")

# Pause to check the database
input("Press Enter to finish...")
