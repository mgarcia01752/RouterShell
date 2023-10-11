#!/bin/bash

# Check if the script is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Function to display VLAN information
show_vlans() {
    echo "VLAN information:"
    ip -o link show type vlan | awk -F'[@ ]' '{print $2, $3}' | sed 's/:$//'
}

# Main script
show_vlans
