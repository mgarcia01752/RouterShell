#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root."
    exit 1
fi

# Detect the Linux distribution
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    case "$ID" in
        ubuntu|debian)
            package_manager="apt"
            ;;
        centos|rhel|fedora)
            package_manager="yum"
            ;;
        opensuse)
            package_manager="zypper"
            ;;
        *)
            echo "Unsupported Linux distribution."
            exit 1
            ;;
    esac
else
    echo "Unable to detect the Linux distribution."
    exit 1
fi

# Prompt the user to choose a DHCP server
echo "Which DHCP server would you like to install?"
echo "1. KEA DHCP (RouterShell not implemented yet)"
echo "2. Dnsmasq"
read -p "Enter the number (1/2): " dhcp_choice

# Install DHCP server based on the user's choice
if [ "$dhcp_choice" == "1" ]; then
    if [ "$package_manager" == "apt" ]; then
        $package_manager update
        $package_manager install -y kea-dhcp4-server kea-dhcp6-server isc-dhcp-client
        echo "KEA DHCP server installed successfully."
    elif [ "$package_manager" == "yum" ]; then
        $package_manager update
        $package_manager install -y kea-dhcp
        echo "KEA DHCP server installed successfully."
    elif [ "$package_manager" == "zypper" ]; then
        $package_manager refresh
        $package_manager install -y kea-dhcp
        echo "KEA DHCP server installed successfully."
    else
        echo "Unsupported package manager for KEA DHCP."
        exit 1
    fi
elif [ "$dhcp_choice" == "2" ]; then
    if [ "$package_manager" == "apt" ]; then
        $package_manager update
        $package_manager install -y dnsmasq
        echo "Dnsmasq installed successfully."
    elif [ "$package_manager" == "yum" ]; then
        $package_manager update
        $package_manager install -y dnsmasq
        echo "Dnsmasq installed successfully."
    elif [ "$package_manager" == "zypper" ]; then
        $package_manager refresh
        $package_manager install -y dnsmasq
        echo "Dnsmasq installed successfully."
    else
        echo "Unsupported package manager for Dnsmasq."
        exit 1
    fi
else
    echo "Invalid choice. Please select 1 or 2."
    exit 1
fi

# Additional setup steps
case "$package_manager" in
    apt|yum|zypper)
        $package_manager update
        $package_manager install -y net-tools traceroute bridge-utils ethtool iproute2 hostapd iw openssl python3
        pip install tabulate prettytable argcomplete cmd2
        ;;
    *)
        echo "Unsupported package manager for additional setup steps."
        exit 1
        ;;
esac

echo "Setup completed successfully."

# Get the absolute path to the project's root directory
ROUTERSHELL_PROJECT_ROOT="${PWD}"

# Update the PYTHONPATH to include the project's root directory
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

echo "Setup completed successfully."