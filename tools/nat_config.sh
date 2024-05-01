#!/bin/bash

# Router Interfaces
GIG0="Gig0"
GIG1="Gig1"

# Router Interface IP Addresses
IP_GIG0="172.16.1.1"
IP_GIG1="172.16.0.1"

# Router Interface MAC Addresses (Replace with actual MAC addresses)
MAC_GIG0="8c:ae:4c:db:5f:8e"
MAC_GIG1="00:24:9b:11:9c:ef"

# Flush existing rules and set default policies
iptables -F
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Enable NAT on Gig1 (inside) interface
iptables -t nat -A POSTROUTING -o $GIG0 -j MASQUERADE

# Allow established and related connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow traffic from Gig1 (inside) to Gig0 (outside)
iptables -A FORWARD -i $GIG1 -o $GIG0 -j ACCEPT

# Allow traffic from Gig0 (outside) to Gig1 (inside) for established connections
iptables -A FORWARD -i $GIG0 -o $GIG1 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Drop all other traffic (you can customize this according to your needs)
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Set up ebtables rules for ARP handling
ebtables -A FORWARD -i $GIG0 -o $GIG1 -j ACCEPT --protocol arp --arp-mac-src $MAC_GIG0
ebtables -A FORWARD -i $GIG1 -o $GIG0 -j ACCEPT --protocol arp --arp-mac-src $MAC_GIG1

echo "iptables and ebtables configuration applied successfully."

sudo iptables -t nat -L
sudo iptables -t nat -vnL
sudo iptables -t nat -L -n -v | grep 'MASQUERADE'
sudo ip nat show
sudo ip -s -s nat show

