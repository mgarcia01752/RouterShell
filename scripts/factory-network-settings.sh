#!/usr/bin/env bash

# Default values
BRIDGE="br0"
IP_ADDRESS="192.168.100.10/24"

# Function to display usage
usage() {
    echo "Usage: $0 [-b bridge_name] [-i network] [-d]"
    echo "  -b bridge_name  Specify the bridge name (default: br0)"
    echo "  -i network      Specify the IP address and subnet (default: 192.168.100.10/24)"
    echo "  -d              Destroy the specified bridge"
    exit 1
}

# Function to create the bridge
create_bridge() {
    ip link show "$BRIDGE" &> /dev/null && {
        ip link set "$BRIDGE" down
        ip link delete "$BRIDGE" type bridge
    }

    ip link add name "$BRIDGE" type bridge

    for PORT in $(ls /sys/class/net | grep -E '^e.*[0-9]+'); do
        ip link set "$PORT" down
        ip link set "$PORT" master "$BRIDGE"
        ip link set "$PORT" up
    done

    ip addr add "$IP_ADDRESS" dev "$BRIDGE"
    ip link set "$BRIDGE" up

    echo "All available Ethernet ports have been bridged together and assigned the IP address $IP_ADDRESS"
}

# Function to destroy the bridge
destroy_bridge() {
    ip link show "$BRIDGE" &> /dev/null || {
        echo "Bridge $BRIDGE does not exist."
        return
    }

    for PORT in $(ls /sys/class/net | grep -E '^e.*[0-9]+'); do
        [[ $(cat /sys/class/net/$PORT/master) == "/sys/class/net/$BRIDGE" ]] && ip link set "$PORT" nomaster
    done

    ip link set "$BRIDGE" down
    ip link delete "$BRIDGE" type bridge

    echo "Bridge $BRIDGE and its associated ports have been removed."
}

# Parse CLI arguments
while getopts ":b:i:d" opt; do
    case "${opt}" in
        b) BRIDGE=${OPTARG} ;;
        i) IP_ADDRESS=${OPTARG} ;;
        d) DESTROY=1 ;;
        *) usage ;;
    esac
done

# Execute the appropriate function
[[ $DESTROY -eq 1 ]] && destroy_bridge || create_bridge
