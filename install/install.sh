#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root."
    exit 1
fi

# Check if port 53 is already in use
if lsof -i :53 >/dev/null 2>&1; then
    echo "Port 53 is already in use and DNSMasq will be using it, Another process may be using it."
    read -p "Do you want to stop and uninstall the process using port 53? (y/n): " choice
    if [ "$choice" == "y" ]; then
        # Find the process using port 53 and kill it
        process_id=$(lsof -t -i :53)
        if [ -n "$process_id" ]; then
            echo "Stopping process with ID $process_id using port 53..."
            kill "$process_id"
            echo "Process killed."
        else
            echo "No process found using port 53."
        fi
    else
        echo "Exiting the script."
        exit 1
    fi
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
        $package_manager install -y lshw            \
                                    net-tools       \
                                    traceroute      \
                                    bridge-utils    \
                                    ethtool         \
                                    iproute2        \
                                    hostapd         \
                                    iw              \
                                    openssl         \
                                    python3         \
                                    pip             \
                                    dnsmasq         \
                                    nmcli
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