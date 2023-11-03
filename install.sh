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

# Additional setup steps
case "$package_manager" in
    apt|yum|zypper)
        $package_manager update
        $package_manager install -y net-tools traceroute bridge-utils ethtool iproute2 hostapd iw openssl python3 pip dnsmasq
        ;;
    *)
        echo "Unsupported package manager for additional setup steps."
        exit 1
        ;;
esac

# Get the absolute path to the project's root directory
ROUTERSHELL_PROJECT_ROOT="${PWD}"

# Update the PYTHONPATH to include the project's root directory
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

echo "Setup completed successfully."