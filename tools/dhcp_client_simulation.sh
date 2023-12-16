#!/bin/bash

# Function to display script usage
display_usage() {
    echo "Usage: $0 -i <main_interface> -n <max_subinterfaces>"
    echo "Example: $0 -i Gig1 -n 20"
}

# Initialize default values
main_interface=""
max_subinterfaces=""

# Parse command-line options
while getopts ":i:n:" opt; do
    case $opt in
        i)
            main_interface="$OPTARG"
            ;;
        n)
            max_subinterfaces="$OPTARG"
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

# Check for the required options
if [ -z "$main_interface" ] || [ -z "$max_subinterfaces" ]; then
    echo "Missing required options."
    display_usage
    exit 1
fi

# Validate user input
if ! [[ "$max_subinterfaces" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid input. Please enter a positive integer for the maximum number of subinterfaces."
    display_usage
    exit 1
fi

# Create subinterfaces based on user input
for ((i = 1; i <= max_subinterfaces; i++)); do
    ip link add link $main_interface name ${main_interface}:$i type vlan id $i
    sleep 1  # Add a delay to allow time for the interface creation
done

# Activate subinterfaces
for ((i = 1; i <= max_subinterfaces; i++)); do
    ip link set ${main_interface}:$i up
done

# Install DHCP client if not already installed
if ! command -v dhclient &> /dev/null; then
    echo "Installing DHCP client..."
    sudo apt-get update
    sudo apt-get install -y isc-dhcp-client
fi

# Configure DHCP on subinterfaces
for ((i = 1; i <= max_subinterfaces; i++)); do
    dhclient ${main_interface}:$i
done

# Display the configured IP addresses
ip address show
