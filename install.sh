#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root. Run it as a regular user."
    exit 1
fi

# Check if pip is already installed
if command -v pip &>/dev/null; then
    echo "pip is already installed."
else
    # Download and install pip locally
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user

    # Add the local pip installation directory to the PATH
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc

    # Check if pip installation was successful
    if command -v pip &>/dev/null; then
        echo "pip installed successfully."
    else
        echo "Failed to install pip. Please check your internet connection and try again."
        exit 1
    fi
fi

# Check if the script is run as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as a regular user, not as root."
    exit 1
fi

# Detect the Linux distribution
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    case "$ID_LIKE" in
        ubuntu|debian)
            package_manager="apt"
            ;;
        centos|rhel|fedora)
            package_manager="yum"
            ;;
        opensuse)
            package_manager="zypper"
            ;;
        raspbian) # Adding Raspberry Pi as a supported distribution
            package_manager="apt"
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
        $package_manager install -y net-tools traceroute bridge-utils ethtool iproute2 hostapd iw openssl python3 dnsmasq
        pip install tabulate prettytable argcomplete cmd2
        ;;
    *)
        echo "Unsupported package manager for additional setup steps."
        exit 1
        ;;
esac

# Change directory permissions to make /etc/dnsmasq.d/ writable
sudo chmod o+w /etc/dnsmasq.d/

# Get the absolute path to the project's root directory
ROUTERSHELL_PROJECT_ROOT="${PWD}"

# Update the PYTHONPATH to include the project's root directory
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

echo "Setup completed successfully."
