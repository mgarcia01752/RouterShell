#!/usr/bin/env bash

# Stop Dnsmasq
sudo systemctl stop dnsmasq

# Remove Dnsmasq
sudo systemctl disable dnsmasq

# Uninstall Dnsmasq
sudo apt remove dnsmasq

# Purge configuration files
sudo apt purge dnsmasq

# Remove any residual packages
sudo apt autoremove

# Reload systemd
sudo systemctl daemon-reload

# Clean up
sudo rm -rf /etc/dnsmasq.d /etc/dnsmasq.conf /var/lib/misc/dnsmasq.leases

echo "Dnsmasq stopped, removed, and uninstalled."
