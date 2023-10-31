#!/bin/bash

# Stop KEA DHCP Server
sudo systemctl stop kea-dhcp4-server
sudo systemctl stop kea-dhcp6-server

# Remove KEA DHCP Server
sudo systemctl disable kea-dhcp4-server
sudo systemctl disable kea-dhcp6-server

# Uninstall KEA DHCP Server
sudo apt remove kea-dhcp4-server kea-dhcp6-server

# Purge configuration files
sudo apt purge kea-dhcp4-server kea-dhcp6-server

# Remove any residual packages
sudo apt autoremove

# Reload systemd
sudo systemctl daemon-reload

# Clean up
sudo rm -rf /etc/kea /var/lib/kea

echo "KEA DHCP Server stopped, removed, and uninstalled."
