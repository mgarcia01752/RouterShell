# RouterShell                                           (WORK IN PROGRESS)

RouterShell is an open-source IOS-like CLI distribution in Python 3. It aims to provide a flexible solution for network administrators and networking enthusiasts, offering a range of features and capabilities tailored to their needs.

RouterShell's key features include:

1. **Interface Configurations:** RouterShell supports various interface configurations, encompassing loopback interfaces, physical interfaces like Ethernet, USB, wireless (WiFi and cellular), bridging, VLANs, NAT (Network Address Translation), and access control list/firewall support. These features enhance its adaptability to different network setups and security requirements.

2. **Physical Interfaces:** RouterShell's compatibility with different physical interfaces, including USB and wireless connections, makes it suitable for various hardware setups.

3. **Loopback Interfaces:** RouterShell allows for creating and configuring loopback interfaces, which are invaluable for network testing and diagnostics.

4. **Bridging:** RouterShell incorporates bridging capabilities, facilitating the seamless connection of disparate network segments, which can be advantageous for complex network topologies.

5. **VLAN Support:** VLAN support is a part of RouterShell's feature set, aiding in network segmentation and organization, especially in more extensive networks.

6. **NAT Support:** RouterShell includes NAT (Network Address Translation) support, which is essential for translating private IP addresses to public IP addresses, a common requirement in home and business network configurations.

7. **Access Control List/Firewall Support:** RouterShell supports access control lists (ACLs) and firewalls, providing enhanced network security and traffic control.

Regarding its intended use:

- **Quick Router Deployment:** RouterShell is designed to expedite router setup using a minimal Linux image, a valuable feature when rapid deployment is crucial.

- **Router-on-a-Stick Configuration:** RouterShell supports the "router-on-a-stick" configuration, useful for scenarios requiring network segmentation.

- **Compatibility with Embedded Router Distributions:** While initially developed with a focus on Ubuntu, RouterShell's lower layers are designed to be OS-agnostic, potentially allowing compatibility with various lightweight Linux distributions.

In conclusion, RouterShell is a router CLI distribution with features well-suited for specific network setups and security requirements. However, it is crucial to thoroughly assess your specific networking needs and consider whether RouterShell aligns with them before selecting it as your networking solution. Its comprehensive feature set, including NAT support and access control list/firewall support, makes it a versatile choice for network administrators and enthusiasts looking to configure and manage network infrastructure efficiently.

## Table of Contents

- [Global Privileged EXEC Commands](doc/cli/global_priv_exec_cmd.md): Learn about global privileged EXEC commands for system-level tasks.

- [ARP (Address Resolution Protocol)](doc/cli/configure/arp.md): Understand ARP and how it works in RouterShell.

- [Bridge Configuration](doc/cli/configure/bridge.md): Configure and manage bridges in RouterShell.

- [DHCPv4/v6 Configuration](doc/cli/configure/dhcp.md): Explore DHCP (Dynamic Host Configuration Protocol) setup for IPv4 and IPv6.

- [Interface Configuration](doc/cli//configureinterface.md): Configure and manage network interfaces in RouterShell.

- [NAT (Network Address Translation)](doc/cli/configure/nat.md): Set up Network Address Translation for your RouterShell router.

- [Route Configuration](doc/cli//configureroute.md): Understand the routing and how to configure it in RouterShell.

- [VLAN Configuration](doc/cli//configurevlan.md): Configure and manage VLANs in your RouterShell network.

- [System Configuration](doc/cli/global/system.md): Learn about system-level configuration options in RouterShell.

- [Wireless Configuration](doc/cli/configure/wireless.md): Explore wireless network configuration in RouterShell.

## Router Configuration Examples

Explore a variety of router configuration examples to help you get started with RouterShell:

These examples cover scenarios like configuring a four-port bridge with VLAN support, setting up a four-port switch, and configuring NAT for a two-port setup. You can access the detailed instructions and information in the respective configuration files.

- [Four-Port Bridge with VLAN Configuration](doc/cli/four_port_bridge_vlan_config.md): This example guides you through setting up a four-port bridge with VLAN support, allowing for network segmentation and efficient traffic management.

- [Four-Port Switch Configuration](doc/cli/four_port_switch_config.md): Learn how to configure a four-port switch, which is essential for creating a network with multiple connected devices.

- [Two-Port NAT Configuration](doc/cli/two_port_nat_config.md): Understand how to set up Network Address Translation (NAT) for a two-port router, enabling the translation of private IP addresses to public IP addresses.

These configuration examples serve as practical guides to help you implement specific networking setups with RouterShell. Refer to the linked documentation files for step-by-step instructions and detailed explanations.

Feel free to explore these examples and adapt them to your networking needs. If you have any questions or need further assistance, don't hesitate to contact our community or project team. Thank you for choosing RouterShell!

## Additional Resources

Please select the specific documentation file you are interested in from the table of contents above to access detailed information and instructions for configuring and using RouterShell.

If you have any questions or need further assistance, please feel free to reach out to our community or project team. Thank you for choosing RouterShell!

## Running RouterShell (Temporary until install script is ready)

[README INSTALLATION](install/README.md)

## Run RouterShell

```bash
./start.sh
```

## [TODO](todo.md)
