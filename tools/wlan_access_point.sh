#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root."
  exit 1
fi

# Set your network details
SSID="YourNetworkName"
PASSPHRASE="YourPassphrase"
INTERFACE="wlan0"
IP_ADDRESS="192.168.1.1/24"

# Stop network managers that may interfere
systemctl stop NetworkManager
systemctl stop wpa_supplicant

# Configure the wireless interface using ip
ip link set $INTERFACE up
ip address add $IP_ADDRESS dev $INTERFACE

# Create a Kea DHCP configuration file
cat <<EOL > /etc/kea/kea-dhcp4.conf
{
  "Dhcp4": {
    "interfaces-config": {
      "interfaces": [ "$INTERFACE" ]
    },
    "subnet4": [
      {
        "subnet": "192.168.1.0/24",
        "pools": [ { "pool": "192.168.1.2 - 192.168.1.254" } ],
        "option-data": [
          {
            "name": "routers",
            "data": "192.168.1.1"
          },
          {
            "name": "domain-name-servers",
            "data": "8.8.8.8, 8.8.4.4"
          }
        ]
      }
    ]
  }
}
EOL

# Start the Kea DHCP server
systemctl start kea-dhcp4

# Create a hostapd configuration file
cat <<EOL > /etc/hostapd/hostapd.conf
interface=$INTERFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSPHRASE
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOL

# Start the access point using hostapd
systemctl start hostapd

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Configure IP tables to allow NAT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Save the IP tables rules
iptables-save > /etc/iptables.ipv4.nat

# Set up IP tables restore on boot
echo "up iptables-restore < /etc/iptables.ipv4.nat" >> /etc/network/interfaces

# Restart networking to apply changes
systemctl restart networking

echo "Wireless Access Point configured successfully!"
