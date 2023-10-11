# NAT Network Address Translation

Setting up Network Address Translation (NAT) on a Linux system involves using the `iptables` firewall rules to allow traffic to pass between the inside and outside interfaces while translating the source IP address of outgoing packets from the inside network to the IP address of the outside interface. In your case, the inside interface is Gig0 with the IP range 10.100.1.100 - 10.100.1.250, and the outside interface is Gig1 with a DHCP-assigned IP address.

## NAT on Linux:

**Step 1: Check the Inside and Outside Interfaces**
Before configuring NAT, make sure that your Linux system recognizes the inside (Gig0) and outside (Gig1) interfaces correctly. You can use the `ifconfig` or `ip addr` command to verify the interface names and IP addresses.

**Step 2: Enable IP Forwarding**
IP forwarding needs to be enabled on your Linux system so that it can act as a router. You can do this by editing the `/etc/sysctl.conf` file:

```bash
sudo nano /etc/sysctl.conf
```

Uncomment or add the following line to enable IP forwarding:

```bash
net.ipv4.ip_forward=1
```

Save and exit the file, then apply the changes with:

```bash
sudo sysctl -p
```

**Step 3: Set Up NAT Rules**
Now, you need to create NAT rules using `iptables` to enable NAT:

```bash
sudo iptables -t nat -A POSTROUTING -o Gig1 -j MASQUERADE
```

This rule tells the system to perform source NAT (MASQUERADE) on packets going out of the Gig1 interface.

**Step 4: Set Up Firewall Rules**
You should also configure your firewall to allow traffic to flow between the inside and outside interfaces. Here's a basic example that allows all outgoing traffic and only established incoming traffic:

The provided `iptables` rules are configuring packet filtering and forwarding for network traffic. Here's a breakdown of each rule:

1. Allow Established and Related Connections:

   ```bash
   sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
   ```

   - This rule allows incoming packets that are part of established or related connections. It's typically used to allow responses to outgoing traffic and traffic related to established connections to pass through the firewall.

2. Allow Incoming Traffic on Interface Gig0:

   ```bash
   sudo iptables -A INPUT -i Gig0 -j ACCEPT
   ```

   - This rule allows all incoming traffic on the `Gig0` interface. Incoming traffic on this interface will be accepted.

3. Allow Forwarding Traffic from Gig0 to Gig1:

   ```bash
   sudo iptables -A FORWARD -i Gig0 -o Gig1 -j ACCEPT
   ```

   - This rule allows traffic to be forwarded from the `Gig0` interface to the `Gig1` interface. It's used for traffic that passes through the router from one interface to another.

These rules seem to be part of a basic network configuration to allow traffic on certain interfaces and permit traffic related to established connections. Please note that these rules should be adapted to your specific network and security requirements.

Additionally, depending on your use case, you might want to configure more rules to specify the types of traffic that are allowed or denied on each interface and ensure that your firewall configuration meets your network's security policies.

These rules allow incoming traffic that is part of an established or related connection and also permit traffic coming from the inside interface (Gig0) to pass through.

**Step 5: Save and Apply the Rules**
To save the `iptables` rules so that they persist across reboots, you can use a tool like `iptables-persistent`:

```bash
sudo apt-get install iptables-persistent
sudo service iptables-persistent save
```

**Step 6: Test the Configuration**
Finally, you should test your NAT configuration by trying to ping an external IP address from a device within the 10.100.1.0/24 range:

```bash
ping 8.8.8.8
```

Ensure that you receive replies from external addresses, indicating that your NAT setup is working correctly.

Please note that this is a basic NAT setup. Depending on your specific requirements and security considerations, you may need to adjust the firewall rules and add more complex configurations to meet your needs. Additionally, make sure to customize these steps according to your Linux distribution and any specific network setup you have.

Certainly, to execute the `iptables` and `ip6tables` commands with administrative privileges (sudo), you can prepend `sudo` before each command. Here's how you can clear all NAT configurations with sudo:

## For IPv4 NAT (SNAT and DNAT):

```bash
# Flush the NAT rules in the nat table
sudo iptables -t nat -F

# Flush the NAT rules in the mangle table (if used for NAT)
sudo iptables -t mangle -F

# Delete any user-defined chains in the nat table (optional)
sudo iptables -t nat -X

# Delete any user-defined chains in the mangle table (optional)
sudo iptables -t mangle -X
```

## For IPv6 NAT (SNAT and DNAT):

```bash
# Flush the NAT rules in the nat table for IPv6
sudo ip6tables -t nat -F

# Delete any user-defined chains in the nat table for IPv6 (optional)
sudo ip6tables -t nat -X
```

Using `sudo` will execute these commands with elevated privileges, which are usually required to modify firewall and NAT configurations. Make sure to enter your password when prompted by `sudo`.

Again, please use caution when clearing NAT configurations, as it can disrupt network traffic temporarily.

## Router CLI Configuration

### NAT Configuration Syntax in this order

```

enable
configure terminal

nat pool <nat-pool-name>

interface <outside-nat-interface-name>
    ip [dhcp-client | address <ipv4-address> <ipv4-subnet>] 
    ip nat outside pool <nat-pool-name> 
    end

interface <inside-nat-interface-name>
    ip address <ipv4-address> <ipv4-subnet>
    ip nat inside pool <nat-pool-name>
    ip dhcp-server pool <dhcp-server-pool-name>
    end

access-list 999 permit $SOURCE_ADDRESS $SUBNET_MASK

ip nat pool <nat-pool-name> <inside-nat-ip-range-ip-start> <inside-nat-ip-range-ip-end> netmask <inside-nat-ip-netmask>
ip nat pool <nat-pool-name> [inside|outside] source list <acl-id> 

```
### Example

For the outside NAT, and IPv4 MUST be assigned either a static address or an address assigned by DHCP

```
enable
configure terminal

nat pool office-nat-pool

rename if enx00249b119cef if-alias Gig0

interface Gig0
    ip address 172.16.0.1 255.255.255.0
    ip nat outside pool office-nat-pool
    end

rename if enx9cebe81be18a if-alias Gig1

interface Gig1
    ip address 192.168.10.1 255.255.255.0
    ip nat inside pool office-nat-pool 
    end

access-list 999 permit
ip nat pool office-nat 10.100.10.50 10.100.10.254 netmask 255.255.255.0
ip nat inside source list 999 pool office-nat
    
```

Certainly, I'll create a user manual in Markdown format based on the provided configuration. Please find the manual below:

# NAT Configuration User Manual

This user manual provides step-by-step instructions for configuring Network Address Translation (NAT) on a router or network device using the command-line interface.

## Table of Contents

1. [Enabling NAT](#enabling-nat)
2. [Configuring NAT Pool](#configuring-nat-pool)
3. [Configuring Outside Interface](#configuring-outside-interface)
4. [Configuring Inside Interface](#configuring-inside-interface)
5. [Defining Access Control List](#defining-access-control-list)
6. [Configuring NAT Pool Range](#configuring-nat-pool-range)
7. [Associating NAT Pool with ACL](#associating-nat-pool-with-acl)

---

## 1. Enabling NAT <a name="enabling-nat"></a>

To enable NAT, follow these steps:

```
enable
configure terminal
```

## 2. Configuring NAT Pool <a name="configuring-nat-pool"></a>

Create a NAT pool with a specific name using the following command:

```
nat pool <nat-pool-name>
```

## 3. Configuring Outside Interface <a name="configuring-outside-interface"></a>

Configure the outside NAT interface. You have two options:

### Option 1: Using DHCP Client

```
interface <outside-nat-interface-name>
    ip dhcp-client
    ip nat outside pool <nat-pool-name>
    end
```

### Option 2: Assigning a Static IP Address

```
interface <outside-nat-interface-name>
    ip address <ipv4-address> <ipv4-subnet>
    ip nat outside pool <nat-pool-name>
    end
```

## 4. Configuring Inside Interface <a name="configuring-inside-interface"></a>

Configure the inside NAT interface with the following commands:

```
interface <inside-nat-interface-name>
    ip address <ipv4-address> <ipv4-subnet>
    ip nat inside pool <nat-pool-name>
    ip dhcp-server pool <dhcp-server-pool-name>
    end
```

## 5. Defining Access Control List <a name="defining-access-control-list"></a>

Create an access control list (ACL) with ID 999 to permit specific source addresses:

```shell
access-list 999 permit $SOURCE_ADDRESS $SUBNET_MASK
```

## 6. Configuring NAT Pool Range <a name="configuring-nat-pool-range"></a>

Define the NAT pool's IP range and netmask:

```shell
ip nat pool <nat-pool-name> <inside-nat-ip-range-ip-start> <inside-nat-ip-range-ip-end> netmask <inside-nat-ip-netmask>
```

## 7. Associating NAT Pool with ACL <a name="associating-nat-pool-with-acl"></a>

Associate the NAT pool with an access control list (ACL) for either inside or outside sources:

```shell
ip nat pool <nat-pool-name> [inside|outside] source list <acl-id>
```

---

This user manual provides a detailed guide for configuring NAT on your router or network device. Follow the steps outlined above to enable NAT and set up NAT pools, interfaces, access control lists, and more to control network traffic and IP address translation.

For any additional assistance or troubleshooting, please refer to the documentation for your specific router or device or contact your network administrator.
