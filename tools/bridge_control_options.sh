#!/usr/bin/env bash

vif_names=("loopback10" "loopback11" "loopback12" "loopback13")

# Function to create virtual interfaces
create_virtual_interfaces() {
  local peers="$1"  # "yes" or "no" to create with or without peers

  for vif in "${vif_names[@]}"; do
    if [ "$peers" == "yes" ]; then
      ip link add "$vif" type veth peer name "$vif"_peer
    else
      ip link add "$vif" type veth
    fi
    ip link set "$vif" up
  done

  local message="Virtual interfaces created"
  [ "$peers" == "yes" ] && message+=" with peers"
  echo "$message: ${vif_names[*]}"
}

# Function to create the bridge and add virtual interfaces
create_bridge() {
  bridge_name="br10"

  # Create the bridge
  ip link add name "$bridge_name" type bridge
  ip link set "$bridge_name" up

  # Add virtual interfaces to the bridge
  for vif in "${vif_names[@]}"; do
    ip link set "$vif" master "$bridge_name"
    ip link set "$vif" up
  done

  echo "Bridge '$bridge_name' created and virtual interfaces added."
}

# Function to delete the bridge and virtual interfaces
delete_bridge() {
  bridge_name="br10"

  # Remove virtual interfaces from the bridge and delete them
  for vif in "${vif_names[@]}"; do
    ip link set "$vif" nomaster
    ip link delete "$vif"
  done

  # Delete the bridge
  ip link set "$bridge_name" down
  ip link delete "$bridge_name"

  echo "Bridge '$bridge_name' and virtual interfaces deleted."
}

# Function to show information about the bridge
show_bridge() {
  bridge_name="br10"

  # Display bridge information
  echo "Bridge Information"
  ip addr show
  echo
  echo
  echo "Bridge Information"
  brctl show
}

# Function to show information about virtual interfaces
show_interfaces() {

  for vif in "${vif_names[@]}"; do
    echo "Interface Information for $vif:"
    ip addr show "$vif"
    echo
  done
}

# Main script
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [-c create_peers | -C create_no_peers | -d destroy | -s show | -i show_interfaces]"
  exit 1
fi

option="$1"

case "$option" in
  "-c" | "create_peers")
    create_virtual_interfaces "yes"
    create_bridge
    ;;
  "-C" | "create_no_peers")
    create_virtual_interfaces "no"
    create_bridge
    ;;
  "-d" | "destroy")
    delete_bridge
    ;;
  "-s" | "show")
    show_bridge
    ;;
  "-i" | "show_interfaces")
    show_interfaces
    ;;
  *)
    echo "Invalid option: $option. Use '-c' or 'create_peers' to create with peers, '-C' or 'create_no_peers' to create without peers, '-d' or 'destroy' to delete, '-s' or 'show' to display bridge info, '-i' or 'show_interfaces' to display interface info."
    exit 1
    ;;
esac

exit 0
