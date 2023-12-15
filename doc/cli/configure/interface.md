# Interface Configuration

```text


   interface vlan <vlan-id [1 - 4096] >
      [no] description <name>
      [no] [mac [auto | <mac-address>]]
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [bridge group <bridge-name>]
      [no] shutdown
   end

   interface loopback <id>
      [no] description <name>
      [no] [mac [auto | <mac-address>]]
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [bridge group <bridge-name>]
      [no] shutdown
   end

   interface <physical_interface>
      [no] description <name>
      [no] [mac [auto | <mac-address>]]      
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [ip proxy-arp]
      [no] [ip nat [inside | outside] pool <nat-pool-name>]
      [no] [ip static-arp <ip-address> <mac-address> [arpa]]
      [no] [duplex [half | full | auto]]
      [no] [speed [10 | 100 | 1000 | 10000 | auto]]
      [no] [bridge group <bridge-name>]
      [no] switchport access-vlan [vlan <vlan-id>]
      [no] shutdown
   end

   ; wireless-wifi
   interface <physical_interface>
      [no] description <name>
      [no] [mac [auto | <mac-address>]]      
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [ip proxy-arp]
      [no] [ip nat [inside | outside] pool <nat-pool-name>]
      [no] [ip static-arp <ip-address> <mac-address> [arpa]]
      [no] wireless wireless-wifi <wifi-policy-name>
      [no] [bridge group <bridge-name>]
      [no] switchport access-vlan [vlan <vlan-id>]
      [no] shutdown
      end


```



## Introduction

Network interfaces are essential components of a network device that enable communication between the device and other network entities. This page provides instructions for configuring network interfaces on a network device.

## Prerequisites

Before configuring network interfaces, ensure you have the necessary information and access to your network device. You should also have a basic understanding of network interface concepts.

## Enabling Interface Configuration

To configure network interfaces on your network device, follow the steps below:

1. Access the device's command-line interface (CLI) by entering the following commands:

   ```shell
   enable
   configure terminal
   ```

   You will enter the configuration mode where you can make changes to the interface settings.

### VLAN Interface Configuration

A VLAN (Virtual LAN) interface allows you to assign a VLAN ID and configure network settings for a specific VLAN. To configure a VLAN interface, follow these steps:

1. Enter the VLAN interface configuration mode by using the following command:

   ```shell
   interface vlan <vlan-id [1 - 4096]>
   ```

   - `<vlan-id>`: Replace this with the VLAN ID (1 - 4096) you want to configure.

2. Provide a name for the VLAN interface using the following command:

   ```shell
   name <name>
   ```

   - `<name>`: Specify the name for the VLAN interface.

3. Configure the MAC address for the VLAN interface (optional) using the following command:

   ```shell
   [no] mac [auto | <mac-address>]
   ```

   - `[no]`: Use the `no` prefix to remove the MAC address configuration.
   - `auto`: Automatically assign a MAC address.
   - `<mac-address>`: Specify a custom MAC address.

4. Configure the IP address and subnet mask for the VLAN interface (optional) using the following command:

   ```shell
   [no] ip address <ip-address> <ip-subnet-mask> [secondary]
   ```

   - `[no]`: Use the `no` prefix to remove the IP address configuration.
   - `<ip-address>`: Specify the IP address for the VLAN interface.
   - `<ip-subnet-mask>`: Specify the subnet mask for the IP address.
   - `secondary`: Use this keyword to configure a secondary IP address.

5. Configure the IPv6 address for the VLAN interface (optional) using the following command:

   ```shell
   [no] ipv6 address <ipv6-ip-address>/<subnet> [secondary]
   ```

   - `[no]`: Use the `no` prefix to remove the IPv6 address configuration.
   - `<ipv6-ip-address>/<subnet>`: Specify the IPv6 address and subnet for the VLAN interface.
   - `secondary`: Use this keyword to configure a secondary IPv6 address.

6. Assign the VLAN interface to a bridge group (optional) using the following command:

   ```shell
   [no] bridge-group <bridge-name>
   ```

   - `[no]`: Use the `no` prefix to remove the interface from the bridge group.
   - `<bridge-name>`: Specify the name of the bridge group.

7. Enable or disable the VLAN interface using the following command:

   ```shell
   [no] shutdown
   ```

8. To remove the VLAN interface configuration entirely, use the following command:

   ```shell
   destroy
   ```

   This command deletes the VLAN interface configuration.

9. Exit the VLAN interface configuration mode when you are done:

   ```shell
   end
   ```

   This will return you to the global configuration mode.

### Loopback Interface Configuration

A loopback interface is a virtual interface used for internal testing and management purposes. To configure a loopback interface, follow these steps:

1. Enter the loopback interface configuration mode by using the following command:

   ```shell
   interface loopback <id>
   ```

   - `<id>`: Replace this with the desired loopback interface ID.

2. Configure the MAC address for the loopback interface (optional) using the following command:

   ```shell
   [no] mac [auto | <mac-address>]
   ```

   - `[no]`: Use the `no` prefix to remove the MAC address configuration.
   - `auto`: Automatically assign a MAC address.
   - `<mac-address>`: Specify a custom MAC address.

3. Configure the IP address and subnet mask for the loopback interface (optional) using the following command:

   ```shell
   [no] ip address <ip-address> <ip-subnet-mask> [secondary]
   ```

   - `[no]`: Use the `no` prefix to remove the IP address configuration.
   - `<ip-address>`: Specify the IP address for the loopback interface.
   - `<ip-subnet-mask>`: Specify the subnet mask for the IP address.
   - `secondary`: Use this keyword to configure a secondary IP address.

4. Configure the IPv6 address for the loopback interface (optional) using the following command:

   ```shell
   [no] ipv6 address <ipv6-ip-address>/<subnet> [secondary]
   ```

   - `[no]`: Use the `no` prefix to remove the IPv6 address configuration.
   - `<ipv6-ip-address>/<subnet>`: Specify the IPv6 address and subnet for the loopback interface.
   - `secondary`: Use this keyword to configure a secondary IPv6 address.

5. Assign the loopback interface to a bridge group (optional) using the following command:

   ```shell
   [no] bridge-group <bridge-name>
   ```

   - `[no]`: Use the `no` prefix to remove the interface from the bridge group.
   - `<bridge-name>`: Specify the name of the bridge group.

6. Enable or disable the loopback interface using the following command:

   ```shell
   [no] shutdown
   ```

7. To remove the loopback interface configuration entirely, use the following command:

   ```shell
   destroy
   ```

   This command deletes the loopback interface configuration.

8. Exit the loopback interface configuration mode when you are done:

   ```shell
   end
   ```

   This will return you to the global configuration mode.

### Physical Interface Configuration

A physical interface connects the network device to the external network. To configure a physical interface, follow these steps:

1. Enter the configuration mode for the physical interface by using the following command:

   ```shell
   interface <physical_interface>
   ```

   - `<physical_interface>`: Replace this with the name of the physical network interface you want to configure.

2. Configure the MAC address for the physical interface (optional) using the following command:

   ```shell
   [no] mac [auto | <mac-address>]
   ```

   - `[no]`: Use the `no` prefix to remove the MAC address configuration.
   - `auto`: Automatically assign a MAC address.
   - `<mac-address>`: Specify a custom MAC address.

3. Configure the IP address and subnet mask for the physical interface (optional) using the following command:

   ```shell
   [no] ip address <ip-address> <ip-subnet-mask> [secondary]
   ```

   - `[no]`: Use the `no` prefix to remove the IP address configuration.
   - `<ip-address>`: Specify the IP address for the physical interface.
   - `<ip-subnet-mask>`: Specify the subnet mask for the IP address.
   - `secondary`: Use this keyword to configure a secondary IP address.

4. Configure the IPv6 address for the physical interface (optional) using the following command:

   ```shell
   [no] ipv6 address <ipv6-ip-address>/<subnet> [secondary]
   ```

   - `[no]`: Use the `no` prefix to remove the IPv6 address configuration.
   - `<ipv6-ip-address>/<subnet>`: Specify the IPv6 address and subnet for the physical interface.
   - `secondary`: Use this keyword to configure a secondary IPv6 address.

5. Configure the duplex mode for the physical interface (optional) using the following command:

   ```shell
   [no] duplex [half | full | auto]
   ```

   - `[no]`: Use the `no` prefix to remove the duplex configuration.
   - `half`: Set the duplex mode to half-duplex.
   - `full`: Set the duplex mode to full-duplex.
   - `auto`: Set the duplex mode to auto-negotiation.

6. Configure the speed for the physical interface (optional) using the following command:

   ```shell
   [no] speed [10 | 100 | 1000 | 10000 | auto]
   ```

   - `[no]`: Use the `no` prefix to remove the speed configuration.
   - `<speed>`: Specify the desired speed (e.g., 10, 100, 1000, 10000, or auto).

7. Assign the physical interface to a bridge group (optional) using the following command:

   ```shell
   [no] bridge-group <bridge-name>
   ```

   - `[no]`: Use the `no` prefix to remove the interface from the bridge group.
   - `<bridge-name>`: Specify the name of the bridge group.

8. Configure the interface as an access port (optional) using the following command:

   ```shell
   [no] switchport mode access [vlan <vlan-id>]
   ```

   - `[no]`: Use the `no` prefix to remove the access port configuration.
   - `switchport mode access`: Set the interface as an access port.
   - `[vlan <vlan-id>]`: Specify the VLAN ID for the access port (optional).

9. Enable or disable the physical interface using the following command:

   ```shell
   [no] shutdown
   ```

10. Exit the physical interface configuration mode when you are done:

    ```shell
    end
    ```

    This will return you to the global configuration mode.

### Conclusion

Configuring network interfaces is crucial for establishing network connectivity and optimizing network performance. By following the steps outlined in this guide, you can customize interface settings on your network device to meet your specific requirements. Always exercise caution when making changes to interface settings, as misconfiguration can impact network connectivity.

```shell
   enable

   configure terminal

   interface vlan <vlan-id [1 - 4096] >
      name <name>
      [no] [mac [auto | <mac-address>]]
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [bridge-group <bridge-name>]
      [no] shutdown
      destroy
      end

   interface loopback <id>
      [no] [mac [auto | <mac-address>]]
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [bridge-group <bridge-name>]
      [no] shutdown
      destroy
      end

   interface <physical_interface>
      [no] [mac [auto | <mac-address>]]      
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] [ip proxy-arp]
      [no] [ip nat [inside | outside] pool <nat-pool-name>]
      [no] [ip static-arp <ip-address> <mac-address> [arpa]]
      [no] [duplex [half | full | auto]]
      [no] [speed [10 | 100 | 1000 | 10000 | auto]]
      [no] [bridge group <bridge-name>]
      [no] switchport access-vlan [vlan <vlan-id>]
      [no] shutdown
      end

   ; wireless-wifi
   interface <physical_interface>
      [no] wireless wireless-wifi <wifi-policy-name>
      [no] shutdown
      end

```
