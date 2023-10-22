# Basic 2-Interface Network Configuration

This is a basic configuration for a router with two interfaces. It includes NAT (Network Address Translation) for internet access, a DHCP server for LAN clients, loopback interface configuration, and interface setup.

## Initial Setup

To start configuring the router, follow these steps:

1. **Access Privileged Exec Mode**: Type `enable` and press Enter to access privileged exec mode.

2. **Enter Global Configuration Mode**: Type `configure terminal` and press Enter to enter global configuration mode.

## NAT Configuration

Create a NAT pool named `home-nat` for translating private LAN IP addresses to a single public IP address for internet access.

```config
nat pool home-nat
```

## DHCP Server Configuration

Configure a DHCP server named `home-lan` for assigning IP addresses to LAN clients. This server will provide IP addresses in the range of `10.1.1.100` to `10.1.1.254` with a subnet mask of `255.255.255.0`. Also, set the default gateway for LAN clients to `10.1.1.1`.

```config
dhcp home-lan
    subnet 10.1.1.0 255.255.255.0
    pool 10.1.1.100 10.1.1.254 255.255.255.0
    option routers 10.1.1.1
    commit
end
```

## Loopback Interface Configuration

Create a loopback interface with the following settings:

- Automatically assign a MAC address.
- Assign the IP address `10.0.0.1` with a subnet mask of `255.255.255.0`.
- Activate the loopback interface.

```config
interface loopback 1
    mac auto
    ip address 10.0.0.1 255.255.255.0
    no shutdown
end
```

## Interface Configuration

### GigabitEthernet 0 (Gig0)

Rename the physical interface `enx3c8cf8f943a2` to `Gig0`. Then, configure the interface with an IP address of `172.16.0.1` and a subnet mask of `255.255.255.0`. Enable NAT for outbound traffic using the `home-nat` pool and activate the interface.

```config
flush enx3c8cf8f943a2
rename if enx3c8cf8f943a2 if-alias Gig0

interface Gig0
    ip address 172.16.0.1 255.255.255.0
    ip nat outside pool-name home-nat
    no shutdown
end
```

### GigabitEthernet 1 (Gig1)

Rename the physical interface `enx00249b119cef` to `Gig1`. Then, configure the interface with an IP address of `10.1.1.1` and a subnet mask of `255.255.255.0`. Enable NAT for inbound traffic using the `home-nat` pool, associate the interface with the `home-lan` DHCP server pool, and activate the interface.

```config
flush enx00249b119cef
rename if enx00249b119cef if-alias Gig1

interface Gig1
    ip address 10.1.1.1 255.255.255.0
    ip nat inside pool-name home-nat
    dhcp-server pool-name home-lan
    no shutdown
end
```

The provided configuration establishes basic network services, including NAT for internet access, DHCP for LAN clients, and loopback and interface setup. Make sure to save the configuration for it to persist across router restarts.

## Full Configuration

Here is the full configuration:

```config
enable
configure terminal

;Network Address Translation
nat pool home-nat

dhcp home-lan
    subnet 10.1.1.0 255.255.255.0
    pool 10.1.1.100 10.1.1.254 255.255.255.0
    option routers 10.1.1.1
    commit
end

interface loopback 1
    mac auto
    ip address 10.0.0.1 255.255.255.0
    no shutdown
end

flush enx8cae4cdb5f8e
rename if enx8cae4cdb5f8e if-alias Gig0

interface Gig0
    ip address 172.16.0.1 255.255.255.0
    ip nat outside pool-name home-nat
    no shutdown
end

flush enx00249b119cef
rename if enx00249b119cef if-alias Gig1

interface Gig1
    ip address 10.1.1.1 255.255.255.0
    ip nat inside pool-name home-nat
    dhcp-server pool-name home-lan
    no shutdown
end
```

This configuration provides the foundation for a simple network setup, and you can build upon it to meet your specific requirements.