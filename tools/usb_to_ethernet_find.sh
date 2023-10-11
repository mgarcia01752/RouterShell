#!/bin/bash

# Function to check if a device is a USB to Ethernet adapter based on bus info
is_usb_to_eth() {
  local bus_info="$1"
  
  # Check if the bus info indicates a USB device
  if [[ "$bus_info" == *"usb"* ]]; then
    return 0  # Return success if it's a USB to Ethernet adapter
  fi
  return 1  # Return failure by default
}

# Get the network interfaces using lshw
network_info=$(lshw -c network)

# Initialize variables to store bus info and interface name
current_bus_info=""
current_interface=""

# Iterate through network interfaces and check if they are USB to Ethernet adapters
while read -r line; do
  if [[ "$line" == *"bus info:"* ]]; then
    # Extract bus info from the line
    bus_info=$(echo "$line" | awk -F ' ' '{print $3}')
    if is_usb_to_eth "$bus_info"; then
      # If it's a USB to Ethernet adapter, store the bus info
      current_bus_info="$bus_info"
    else
      # If it's not a USB to Ethernet adapter, reset the stored bus info
      current_bus_info=""
    fi
  elif [[ "$line" == *"logical name:"* ]]; then
    # Extract the logical name from the line
    current_interface=$(echo "$line" | awk -F ' ' '{print $3}')
    if [[ -n "$current_bus_info" ]]; then
      # If a USB to Ethernet adapter was found, print its interface name
      echo "USB to Ethernet adapter found: $current_interface"
      # Reset the stored bus info for the next iteration
      current_bus_info=""
    fi
  fi
done <<< "$network_info"
