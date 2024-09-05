#!/usr/bin/env bash

# Function to create bridges and virtual interfaces
create_network() {
  local vlan="$1"
  local nvif="$2"
  local ip_cidr="$3"
  local gateway="$4"
  local bridge_name="br$vlan"
  
  # Extract IP address and subnet mask from CIDR notation
  ip_addr=$(echo "$ip_cidr" | cut -d'/' -f1)
  subnet_mask=$(echo "$ip_cidr" | cut -d'/' -f2)
  
  # Create the bridge and assign the VLAN
  brctl addbr "$bridge_name"
  ip link set "$bridge_name" up
  ip link add link "$bridge_name" name "$bridge_name.$vlan" type vlan id "$vlan"
  ip link set "$bridge_name.$vlan" up
  
  # Create and configure virtual interfaces for the bridge
  for i in $(seq 0 $((nvif - 1))); do
    ip link add link "$bridge_name" name "$bridge_name-vif$i" type veth peer name "$bridge_name-vif$i-peer"
    ip link set "$bridge_name-vif$i" up
    ip link set "$bridge_name-vif$i-peer" up
    ip link set "$bridge_name-vif$i" master "$bridge_name"
    ip link set "$bridge_name-vif$i-peer" master "$bridge_name"
  done
  
  # Set the IP address and default gateway for the bridge
  ip addr add "$ip_addr/$subnet_mask" dev "$bridge_name.$vlan"
  ip route add default via "$gateway" dev "$bridge_name.$vlan"
}

# Function to destroy bridges and virtual interfaces
destroy_network() {
  local vlan="$1"
  local bridge_name="br$vlan"

  # Turn down the bridge interface
  ip link set "$bridge_name" down

  # Remove virtual interfaces
  for iface in $(ip link show | grep "$bridge_name-vif" | awk -F: '{print $2}' | awk '{print $1}'); do
    ip link delete "$iface"
  done

  # Remove VLAN interface
  ip link delete "$bridge_name.$vlan"

  # Remove the bridge itself
  brctl delbr "$bridge_name"

  echo "Network with VLAN $vlan and bridge $bridge_name destroyed."
}

# Function to display the current network configuration
view_network() {
  local vlan="$1"
  local bridge_name="br$vlan"

  echo "Network Configuration for VLAN $vlan:"
  echo "Bridge Name: $bridge_name"
  
  # Display virtual interfaces
  echo "Virtual Interfaces:"
  for iface in $(ip link show | grep "$bridge_name-vif" | awk -F: '{print $2}' | awk '{print $1}'); do
    echo "  $iface"
  done
  
  # Display VLAN interface
  echo "VLAN Interface: $bridge_name.$vlan"

  # Display IP address and default gateway
  local ip_info=$(ip addr show dev "$bridge_name.$vlan" | grep "inet ")
  local gateway_info=$(ip route show dev "$bridge_name.$vlan" | grep "default via")
  
  echo "IP Address and Subnet Mask: $ip_info"
  echo "Default Gateway: $gateway_info"
}

# Display usage information
usage() {
  echo "Usage: $0 -c|-d|-v -vlan VLAN_ID -nvif NUM_VIF -ip IP_ADDRESS -gw GATEWAY [-debug]"
  echo "  -c          Create network"
  echo "  -d          Destroy network"
  echo "  -v          View network configuration"
  echo "  -vlan       VLAN ID (e.g., 1000)"
  echo "  -nvif       Number of virtual interfaces (e.g., 4)"
  echo "  -ip         IP address in CIDR notation (e.g., 192.168.1.1/24)"
  echo "  -gw         Gateway IP address (e.g., 192.168.1.254)"
  echo "  -debug      Debug mode (optional)"
  exit 1
}

# Debug function to display options
debug_options() {
  echo "Action: $action"
  echo "VLAN ID: $vlan"
  echo "Number of VIFs: $nvif"
  echo "IP Address: $ip_cidr"
  echo "Gateway: $gateway"
  echo "Debug Mode: $debug"
}

# Initialize debug mode as false
debug="false"

# Check for command-line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c)
      action="-c"
      ;;
    -d)
      action="-d"
      ;;
    -v)
      action="-v"
      ;;
    -vlan)
      vlan="$2"
      shift
      ;;
    -nvif)
      nvif="$2"
      shift
      ;;
    -ip)
      ip_cidr="$2"
      shift
      ;;
    -gw)
      gateway="$2"
      shift
      ;;
    -debug)
      debug="true"
      ;;
    *)
      usage
      ;;
  esac
  shift
done

# If debug mode is enabled, display options and exit
if [ "$debug" == "true" ]; then
  debug_options
  exit 0
fi

# Check if the action is "-c" (create), "-d" (destroy), or "-v" (view)
case "$action" in
  -c)
    create_network "$vlan" "$nvif" "$ip_cidr" "$gateway"
    ;;
  -d)
    destroy_network "$vlan"
    ;;
  -v)
    view_network "$vlan"
    ;;
  *)
    usage
    ;;
esac
