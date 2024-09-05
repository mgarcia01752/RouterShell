# Ethernet Configuration Guide

## Configuration Options

```text
interface <physical_interface>
   [no] description <name>
   [no] mac [auto | <mac-address>]
   [no] ip address <ip-address>/<CIDR> [secondary]
   [no] ip proxy-arp
   [no] ip nat [inside | outside] pool <nat-pool-name>
   [no] ip static-arp <ip-address> <mac-address> [arpa]
   [no] ip dhcp-server pool-name <dhcp-pool-name>
   [no] duplex [half | full | auto]
   [no] speed [10 | 100 | 1000 | 2500 | 10000 | auto]
   [no] bridge group <bridge-name>
   [no] switchport access-vlan [vlan <vlan-id>]
   [no] shutdown
end
```

```text
interface <physical_interface>
   [no] ipv6 address <ipv6-ip-address>/<CIDR> [secondary]
end
```

### Step-by-Step Configuration

1. **Enter Configuration Mode**:

   Entering the configuration mode is the first step to modify the Ethernet interface settings. This command provides access to the configuration terminal where all interface-specific settings can be applied.

   ```shell
   configure terminal
   ```

   The prompt will change to `Router(config)#`.

2. **Select the Interface**:

   Select the specific physical interface to configure.

   ```shell
   interface eth0
   ```

   The prompt will change to `Router(config-eth)#`.

3. **Add or Remove a Description** (Optional):

   **Add a Description:**

   Adding a description to an interface helps in identifying its purpose, which is especially useful in large network environments.

   ```shell
   description <description>
   ```

   **Remove a Description:**

   If you need to remove the description for any reason, you can use the `no` command.

   ```shell
   no description
   ```

4. **Assign a MAC Address**:

   **Auto Assign a MAC Address:**

   Automatically assigns a MAC address to the interface, which is useful for dynamically configured environments.

   ```shell
   mac auto
   ```

   **Assign a Specific MAC Address:**

   Manually assign a specific MAC address to the interface. This can be useful for certain network configurations requiring static MAC addresses.

   ```shell
   mac <mac-address>
   ```

   **Remove MAC Address Configuration:**

   To remove the manually assigned MAC address, you can reset it using the `no` command.

   ```shell
   no mac
   ```

5. **Assign an IPv4 Address**:

   **Primary IPv4 Address:**

   Assign a primary IP address to the interface to enable communication within the network.

   ```shell
   ip address <ip-address>/<CIDR>
   ```

   **Secondary IPv4 Address:**

   Assign a secondary IP address for the interface, which is useful for multi-homing or additional routing purposes.

   ```shell
   ip address <ip-address>/<CIDR> secondary
   ```

   **Remove IPv4 Address Configuration:**

   To remove any assigned IP address:

   ```shell
   no ip address <ip-address>/<CIDR>
   ```

6. **Assign an IPv6 Address**:

   **Primary IPv6 Address:**

   Configure an IPv6 address for the interface to enable communication over an IPv6 network.

   ```shell
   ipv6 address <ipv6-ip-address>/<CIDR>
   ```

   **Secondary IPv6 Address:**

   Assign a secondary IPv6 address to the interface.

   ```shell
   ipv6 address <ipv6-ip-address>/<CIDR> secondary
   ```

   **Remove IPv6 Address Configuration:**

   To remove the IPv6 address:

   ```shell
   no ipv6 address <ipv6-ip-address>/<CIDR>
   ```

7. **Enable or Disable Proxy ARP**:

   **Enable Proxy ARP:**

   Proxy ARP allows a router to respond to ARP requests for hosts that are not on the same subnet. This is useful in certain network setups where subnets are bridged.

   ```shell
   ip proxy-arp
   ```

   **Disable Proxy ARP:**

   Disabling proxy ARP can enhance security by preventing ARP spoofing attacks.

   ```shell
   no ip proxy-arp
   ```

8. **Configure NAT**:

   **Configure NAT Inside/Outside:**

   Network Address Translation (NAT) allows multiple devices on a local network to share a single public IP address. Configure NAT to specify the role of the interface.

   ```shell
   ip nat inside pool <nat-pool-name>
   ip nat outside pool <nat-pool-name>
   ```

   **Remove NAT Configuration:**

   To remove NAT configuration:

   ```shell
   no ip nat inside pool <nat-pool-name>
   no ip nat outside pool <nat-pool-name>
   ```

9. **Configure Static ARP**:

   **Set Static ARP:**

   Manually map an IP address to a MAC address, ensuring that certain devices always use the same ARP entries.

   ```shell
   ip static-arp <ip-address> <mac-address> arpa
   ```

   **Remove Static ARP Configuration:**

   To remove static ARP entries:

   ```shell
   no ip static-arp <ip-address> <mac-address> arpa
   ```

10. **Set Duplex Mode**:

    **Configure Duplex Mode:**

    Set the duplex mode of the interface to half, full, or auto, based on network requirements.

    ```shell
    duplex [half | full | auto]
    ```

    **Remove Duplex Configuration:**

    To reset the duplex configuration:

    ```shell
    no duplex
    ```

11. **Set Interface Speed**:

    **Configure Interface Speed:**

    Set the speed of the interface. Supported speeds include 10, 100, 1000, 2500, and 10000 Mbps, as well as auto-negotiation.

    ```shell
    speed [10 | 100 | 1000 | 2500 | 10000 | auto]
    ```

    **Remove Speed Configuration:**

    To reset the interface speed configuration:

    ```shell
    no speed
    ```

12. **Add Interface to Bridge Group**:

    **Configure Bridge Group:**

    Assign the interface to a bridge group, allowing it to participate in bridging.

    ```shell
    bridge group <bridge-name>
    ```

    **Remove Bridge Group Configuration:**

    To remove the interface from the bridge group:

    ```shell
    no bridge group <bridge-name>
    ```

13. **Configure Switchport Access VLAN**:

    **Set Access VLAN:**

    Assign the interface to a VLAN, which is essential for VLAN tagging and segregation.

    ```shell
    switchport access-vlan vlan <vlan-id>
    ```

    **Remove Access VLAN Configuration:**

    To remove the VLAN assignment:

    ```shell
    no switchport access-vlan
    ```

14. **Shutdown or No Shutdown Interface**:

    **Shutdown Interface:**

    Disabling the interface can be used for security or maintenance purposes.

    ```shell
    shutdown
    ```

    **Enable Interface:**

    Bring up an interface that has been shut down.

    ```shell
    no shutdown
    ```

### Detailed Commands and Examples

1. **Adding a Description**:

   ```shell
   configure terminal
   interface eth0
   description Uplink to core switch
   end
   ```

2. **Auto Assign MAC Address**:

   ```shell
   configure terminal
   interface eth0
   mac auto
   end
   ```

3. **Assigning an IPv4 Address**:

   ```shell
   configure terminal
   interface eth0
   ip address 192.168.1.1/24
   end
   ```

4. **Assigning a Secondary IPv4 Address**:

   ```shell
   configure terminal
   interface eth0
   ip address 192.168.1.2/24 secondary
   end
   ```

5. **Setting Duplex Mode to Full**:

   ```shell
   configure terminal
   interface eth0
   duplex full
   end
   ```

6. **Setting Interface Speed to 1000 Mbps**:

   ```shell
   configure terminal
   interface eth0
   speed 1000
   end
   ```

7. **Setting Interface Speed to 2500 Mbps**:

   ```shell
   configure terminal
   interface eth0
   speed 2500
   end
   ```

8. **Adding Interface to Bridge Group**:

   ```shell
   configure terminal
   interface eth0
   bridge group bridge1
   end
   ```

9. **Configuring Switchport Access VLAN**:

   ```shell
   configure terminal
   interface eth0
   switchport access-vlan vlan 10
   end
   ```

By following these detailed steps and examples, you can configure Ethernet interfaces effectively for a variety of network scenarios. The prompt will guide you through each step, changing to `Router(config-eth)#` when configuring specific interface settings.