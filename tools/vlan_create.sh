#!/bin/bash

# Check if the script is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Function to list available network interfaces
list_interfaces() {
    echo "Available network interfaces:"
    ip -o link show | awk -F': ' '{print $2}'
}

# Function to create a VLAN interface
create_vlan() {
    interface="$1"
    vlan_id="$2"

    # Check if the VLAN ID already exists
    existing_vlans=$(ip -d link show type vlan | grep "vlan$id")
    if [[ $existing_vlans =~ vlan$id ]]; then
        echo "VLAN ID $vlan_id already exists."
        exit 1
    fi

    # Create the VLAN interface
    ip link add link "$interface" name "vlan$vlan_id" type vlan id "$vlan_id"

    # Bring up the VLAN interface
    ip link set "vlan$vlan_id" up

    echo "Created VLAN interface vlan$vlan_id"
}

# Main script
list_interfaces

while true; do
    read -p "Enter the name of the physical interface: " interface

    if [ -z "$interface" ]; then
        echo "Please enter a valid interface name."
    elif ! ip link show dev "$interface" &>/dev/null; then
        echo "Interface $interface does not exist."
    else
        break
    fi
done

while true; do
    read -p "Enter the VLAN ID you want to create: " vlan_id

    if [ -z "$vlan_id" ]; then
        echo "Please enter a valid VLAN ID."
    else
        create_vlan "$interface" "$vlan_id"
        break
    fi
done
