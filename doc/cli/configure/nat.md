# NAT Configuration

This page provides step-by-step instructions for configuring Network Address Translation (NAT) on a router or network device using the command-line interface.

## Table of Contents

- [NAT Configuration](#nat-configuration)
  - [Table of Contents](#table-of-contents)
  - [1. Enabling NAT ](#1-enabling-nat-)
  - [2. Configuring NAT Pool ](#2-configuring-nat-pool-)
  - [3. Configuring Outside Interface ](#3-configuring-outside-interface-)
    - [Option 1: Using DHCP Client](#option-1-using-dhcp-client)
    - [Option 2: Assigning a Static IP Address](#option-2-assigning-a-static-ip-address)
  - [4. Configuring Inside Interface ](#4-configuring-inside-interface-)
  - [5. Defining Access Control List ](#5-defining-access-control-list-)
  - [6. Configuring NAT Pool Range ](#6-configuring-nat-pool-range-)
  - [7. Associating NAT Pool with ACL ](#7-associating-nat-pool-with-acl-)
  - [Full Configuration](#full-configuration)

---

## 1. Enabling NAT <a name="enabling-nat"></a>

To enable NAT, follow these steps:

```shell
enable
configure terminal
```

## 2. Configuring NAT Pool <a name="configuring-nat-pool"></a>

Create a NAT pool with a specific name using the following command:

```config
nat pool-name <nat-pool-name>
```

## 3. Configuring Outside Interface <a name="configuring-outside-interface"></a>

Configure the outside NAT interface. You have two options:

### Option 1: Using DHCP Client

```config
interface <outside-nat-interface-name>
    ip dhcp-client
    ip nat outside pool-name <nat-pool-name>
    end
```

### Option 2: Assigning a Static IP Address

```config
interface <outside-nat-interface-name>
    ip address <ipv4-address> <ipv4-subnet>
    ip nat outside pool-name <nat-pool-name>
    end
```

## 4. Configuring Inside Interface <a name="configuring-inside-interface"></a>

Configure the inside NAT interface with the following commands:

```config
interface <inside-nat-interface-name>
    ip address <ipv4-address> <ipv4-subnet>
    ip nat inside pool-name <nat-pool-name>
    ip dhcp-server pool-name <dhcp-server-pool-name>
    end
```

## 5. Defining Access Control List <a name="defining-access-control-list"></a>

Create an access control list (ACL) with ID 999 to permit specific source addresses:

```config
access-list 999 permit $SOURCE_ADDRESS $SUBNET_MASK
```

## 6. Configuring NAT Pool Range <a name="configuring-nat-pool-range"></a>

Define the NAT pool's IP range and netmask:

```config
ip nat pool <nat-pool-name> <inside-nat-ip-range-ip-start> <inside-nat-ip-range-ip-end> netmask <inside-nat-ip-netmask>
```

## 7. Associating NAT Pool with ACL <a name="associating-nat-pool-with-acl"></a>

Associate the NAT pool with an access control list (ACL) for either inside or outside sources:

```config
ip nat pool <nat-pool-name> [inside|outside] source list <acl-id>
```

---

## Full Configuration

```bash

; When negating, user MUST remove pool from interfaces first
[no] ip nat pool <nat-pool-name>

interface <inside-nat-interface-name>
    
    #; Optional ip address when selecting the nat outside pool
    ip address <ipv4-address> <ipv4-subnet>

    [no] ip nat [inside | outside] pool <nat-pool-name>
    
    #; Optional dhcp-server pool when selecting nat inside pool
    ip dhcp-server pool <dhcp-server-pool-name>
end

access-list 999 permit $SOURCE_ADDRESS $SUBNET_MASK

```

[NAT-IOS](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr/command/ipaddr-cr-book/ipaddr-i4.html)

This user manual provides a detailed guide for configuring NAT on your router or network device. Follow the steps outlined above to enable NAT and set up NAT pools, interfaces, access control lists, and more to control network traffic and IP address translation.

For any additional assistance or troubleshooting, please refer to the documentation for your specific router or device or contact your network administrator.
