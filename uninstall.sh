#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root. Run it as a regular user."
    exit 1
fi

# Uninstall specific packages
packages_to_uninstall="net-tools traceroute bridge-utils ethtool iproute2 hostapd iw openssl python3 dnsmasq"

for package in $packages_to_uninstall; do
    if dpkg -l | grep -q "ii  $package"; then
        sudo apt remove $package -y
        sudo apt purge $package -y
    fi
done

# Uninstall pip
echo "Uninstalling pip..."
pip uninstall pip -y

# Remove the added PATH from .bashrc
sed -i '/export PATH=\$HOME\/.local\/bin:\$PATH/d' ~/.bashrc

echo "Uninstallation completed successfully."
