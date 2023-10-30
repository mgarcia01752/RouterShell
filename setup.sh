#!/bin/bash

########################
# UBUNTU INSTALLATION  #
########################

# Update package lists
sudo apt update

# Network Management
sudo apt install -y net-tools
sudo apt install -y traceroute
sudo apt install -y bridge-utils
sudo apt install -y ethtool
sudo apt install -y iproute2

# DHCP ISC Servers/Clents
sudo apt install -y kea-dhcp4-server
sudo apt install -y kea-dhcp6-server
sudo apt install -y isc-dhcp-client

# Wireless
sudo apt install -y hostapd
sudo apt install -y iw

# Security
sudo apt install -y openssl

# Install Python libraries with specific versions
sudo apt install -y python3
pip install tabulate
pip install prettytable
pip install argcomplete
pip install cmd2

echo "Setup completed successfully."

# Get the absolute path to the project's root directory
ROUTERSHELL_PROJECT_ROOT="${PWD}

# Update the PYTHONPATH to include the project's root directory
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

