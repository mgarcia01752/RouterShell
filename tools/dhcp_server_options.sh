#!/usr/bin/env bash

# Default values for DHCP settings
interface="enx3c8cf8f943a2"
subnet="172.16.0.0"
netmask="255.255.255.0"
range_start="172.16.0.2"
range_end="172.16.0.253"
gateway="172.16.0.1"
dns_servers="8.8.8.8"
enable_dhcp=false
disable_dhcp=false

# Function to show script usage
show_usage() {
    echo "Usage: $0 [-e] [-d] [-i interface] [-s subnet] [-m netmask] [-r range_start] [-R range_end] [-g gateway] [-n dns_servers]"
    echo "  -e               Enable DHCP server"
    echo "  -d               Disable DHCP server"
    echo "  -i interface     Network interface to listen on (default: ${interface})"
    echo "  -s subnet        Subnet (default: ${subnet})"
    echo "  -m netmask       Netmask (default: ${netmask})"
    echo "  -r range_start   IP address range start (default: ${range_start})"
    echo "  -R range_end     IP address range end (default: ${range_end})"
    echo "  -g gateway       Gateway IP address (default: ${gateway})"
    echo "  -n dns_servers   DNS server(s) (default: ${dns_servers})"
    exit 1
}

# Parse command-line options
while getopts "edi:s:m:r:R:g:n:" opt; do
    case $opt in
        e)
            enable_dhcp=true
            ;;
        d)
            disable_dhcp=true
            ;;
        i)
            interface="$OPTARG"
            ;;
        s)
            subnet="$OPTARG"
            ;;
        m)
            netmask="$OPTARG"
            ;;
        r)
            range_start="$OPTARG"
            ;;
        R)
            range_end="$OPTARG"
            ;;
        g)
            gateway="$OPTARG"
            ;;
        n)
            dns_servers="$OPTARG"
            ;;
        \?)
            show_usage
            ;;
    esac
done

# Install DHCP Server if not already installed
if ! dpkg -l | grep -q "isc-dhcp-server"; then
    echo "Installing ISC DHCP Server..."
    apt-get update
    apt-get install -y isc-dhcp-server
fi

# Configuration file for DHCPv4
dhcp_config="/etc/dhcp/dhcpd.conf"

# Enable DHCP server
enable_dhcp_server() {
    # Create DHCP configuration file
    cat <<EOL > "$dhcp_config"
    subnet $subnet netmask $netmask {
        range $range_start $range_end;
        option routers $gateway;
        option domain-name-servers $dns_servers;
        default-lease-time 600;
        max-lease-time 7200;
    }
EOL
    # Configure the DHCP server to listen on the specified interface
    echo "INTERFACESv4=\"$interface\"" >> /etc/default/isc-dhcp-server

    # Start the DHCP server
    systemctl start isc-dhcp-server

    # Enable the DHCP server to start on boot
    systemctl enable isc-dhcp-server

    echo "DHCPv4 server enabled for $interface."
}

# Disable DHCP server
disable_dhcp_server() {
    # Stop the DHCP server
    systemctl stop isc-dhcp-server

    # Disable the DHCP server from starting on boot
    systemctl disable isc-dhcp-server

    # Remove the DHCP configuration file
    rm -f "$dhcp_config"

    echo "DHCPv4 server disabled for $interface."
}

# Enable or disable DHCP server based on command-line options
if $enable_dhcp; then
    enable_dhcp_server
elif $disable_dhcp; then
    disable_dhcp_server
else
    show_usage
fi
