#!/usr/bin/env bash

# Function to list available network interfaces
list_interfaces() {
    echo "Available network interfaces:"
    echo "-----------------------------"
    interfaces=($(ip link show | awk -F ': ' '{print $2}' | grep -v lo))
    for ((i = 0; i < ${#interfaces[@]}; i++)); do
        echo "$i: ${interfaces[i]}"
    done
}

# Function to create NAT
create_nat() {
    list_interfaces
    echo
    read -p "Enter the number of the internal interface (e.g., 0, 1, etc.): " internal_index

    if [[ ! $internal_index =~ ^[0-9]+$ || $internal_index -ge ${#interfaces[@]} ]]; then
        echo "Invalid input. Please select a valid interface number."
        return
    fi

    internal_interface="${interfaces[internal_index]}"

    # Find the first non-loopback interface as the external interface
    external_interface=$(ip link show | awk -F ': ' '{print $2}' | grep -v lo | grep -v "$internal_interface" | head -n 1)

    if [[ -z "$external_interface" ]]; then
        echo "Error: No suitable external interface found."
        return
    fi

    echo "Configuring NAT on $internal_interface (internal) and $external_interface (external)..."
    
    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward
    
    # Enable masquerading (SNAT) for outbound traffic
    iptables -t nat -A POSTROUTING -o $external_interface -j MASQUERADE
    
    # Check if the directory for iptables rules exists, and create it if necessary
    if [[ ! -d /etc/iptables ]]; then
        mkdir /etc/iptables
    fi
    
    # Save the iptables rules to make them persistent across reboots
    iptables-save > /etc/iptables/rules.v4
    
    echo "NAT configuration is complete."
}

# Function to destroy NAT
destroy_nat() {
    echo "Destroying NAT configuration..."
    
    # Disable IP forwarding
    echo 0 > /proc/sys/net/ipv4/ip_forward
    
    # Flush and delete NAT rules
    iptables -t nat -F
    iptables -t nat -X

    # Check if the directory for iptables rules exists
    if [[ -d /etc/iptables ]]; then
        # Delete the saved iptables rules file
        rm /etc/iptables/rules.v4
    fi
    
    echo "NAT configuration has been destroyed."
}

# Main menu
while true; do
    echo
    echo "Network Address Translation (NAT) Configuration"
    echo "--------------------------------------------"
    echo "1. Create NAT"
    echo "2. Destroy NAT"
    echo "3. Exit"
    read -p "Select an option (1/2/3): " choice

    case $choice in
        1)
            create_nat
            ;;
        2)
            destroy_nat
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select a valid option."
            ;;
    esac
done
