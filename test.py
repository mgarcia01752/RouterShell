from lib.db.sqlite_db.router_shell_db import RouterShellDB
from lib.network_manager.network_operations.bridge.bridge import STP_STATE, BridgeProtocol


# Test data
bridge_name = "brlan0"
description = "Test Bridge Insert"
protocol = BridgeProtocol.IEEE_802_1D
stp_status = STP_STATE.STP_ENABLE
management_inet = '192.168.200.1'
shutdown_status = True

# Insert a new bridge
insert_result = RouterShellDB().insert_interface_bridge(bridge_name, shutdown_status)
print(f"Insert result: {insert_result}")

# Pause to check the database
input("Press Enter to continue to the next step...")

# Update the bridge
update_result = RouterShellDB().update_bridge(
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

# Delete the bridge
delete_result = RouterShellDB().delete_interface_bridge(bridge_name)
print(f"Delete result: {delete_result}")

# Pause to check the database
input("Press Enter to finish...")
