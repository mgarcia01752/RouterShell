#!/usr/bin/env bash

# Check if the script is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Function to display existing VLAN interfaces
list_existing_vlans() {
    echo "Existing VLAN interfaces:"
    ip -o link show type vlan | awk -F': ' '{split($2, a, "@"); print a[1] " -> " a[2]}'
}

# Main script
list_existing_vlans

# Ask the user to select a VLAN to delete
read -p "Enter the VLAN ID you want to remove: " vlan_id

# Check if the VLAN interface exists
if ip -o link show | grep -q "vlan$vlan_id@"; then
    ip link delete "vlan$vlan_id"
    if [[ $? -eq 0 ]]; then
        echo "Removed VLAN interface vlan$vlan_id"
    else
        echo "Failed to remove VLAN interface vlan$vlan_id"
    fi
else
    echo "VLAN interface vlan$vlan_id does not exist."
fi
