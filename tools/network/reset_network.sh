#!/usr/bin/env bash

# Remove all VLANs
for vlan in $(ls /proc/net/vlan/ | grep ^vlan); do
    sudo vconfig rem $vlan
done

# Remove all bridges
for bridge in $(brctl show | awk 'NR>1 {print $1}'); do
    sudo brctl delbr $bridge
done

# Reset IPtables Rules
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo iptables -t mangle -F
sudo iptables -t mangle -X
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT

# Reset IPv6tables Rules (if using IPv6)
sudo ip6tables -F
sudo ip6tables -X
sudo ip6tables -t nat -F
sudo ip6tables -t nat -X
sudo ip6tables -t mangle -F
sudo ip6tables -t mangle -X
sudo ip6tables -P INPUT ACCEPT
sudo ip6tables -P FORWARD ACCEPT
sudo ip6tables -P OUTPUT ACCEPT

# Flush Route Table
sudo ip route flush table all

# Restart Network Interfaces
sudo ifdown -a
sudo ifup -a

# Restart Networking Service
if command -v service &> /dev/null; then
    sudo service networking restart
elif command -v systemctl &> /dev/null; then
    sudo systemctl restart networking
else
    echo "Unable to determine the service management tool. Please restart networking manually."
fi

echo "Networking stack and VLANs/bridges reset completed."
