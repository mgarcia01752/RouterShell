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

# DHCP Servers
sudo apt install -y kea-dhcp4-server
sudo apt install -y kea-dhcp6-server

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

echo "Setup completed successfully."

# Get the absolute path to the project's root directory
ROUTER_CLI_PROJECT_ROOT="/home/dev01/Projects/Linux-Router-CLIv3"

# Update the PYTHONPATH to include the project's root directory
export PYTHONPATH="${PYTHONPATH}:${ROUTER_CLI_PROJECT_ROOT}:${ROUTER_CLI_PROJECT_ROOT}/src:${ROUTER_CLI_PROJECT_ROOT}/lib:${ROUTER_CLI_PROJECT_ROOT}/test"

