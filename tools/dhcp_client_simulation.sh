#!/usr/bin/env bash

# Function to display script usage
display_usage() {
    echo "Usage: $0 -n <num_interfaces>"
    echo "Example: $0 -n 10"
}

# Initialize default values
num_interfaces=""

# Parse command-line options
while getopts ":n:" opt; do
    case $opt in
        n)
            num_interfaces="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            display_usage
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument."
            display_usage
            exit 1
            ;;
    esac
done

# Check for the required option
if [ -z "$num_interfaces" ]; then
    echo "Missing required option."
    display_usage
    exit 1
fi

# Validate user input
if ! [[ "$num_interfaces" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid input. Please enter a positive integer for the number of loopback interfaces."
    display_usage
    exit 1
fi

# Create loopback interfaces based on user input
for ((i = 1; i <= num_interfaces; i++)); do
    ip link add lo$i type dummy
done

# Activate loopback interfaces
for ((i = 1; i <= num_interfaces; i++)); do
    ip link set lo$i up
done

# Install DHCP client if not already installed
if ! command -v dhclient &> /dev/null; then
    echo "Installing DHCP client..."
    sudo apt-get update
    sudo apt-get install -y isc-dhcp-client
fi

# Configure DHCP on loopback interfaces
for ((i = 1; i <= num_interfaces; i++)); do
    dhclient lo$i
done

# Display the configured IP addresses
ip address show
