# DHCP Server DNSMasq Configuration Guide

This wiki provides a detailed guide on configuring a DHCP server using DNSMasq for both IPv4 and IPv6, including dual-stack and multiple interface scenarios.

## Global Configuration

```shell
cls
configure terminal

dhcp global
    option time-servers 216.239.35.8
end
```

### Explanation:

- This sets global DHCP options. In this example, it configures a time server for DHCP clients.

## IPv4

```shell
cls
configure terminal

! Create DHCP Pools
dhcp dhcpv4-home-office
    subnet 172.16.0.0/24
    pool 172.16.0.50 172.16.60.254 255.255.255.0
    option routers 172.16.0.1
end

! Apply DHCP Pool to Interface
interface Gig0
    ip address 172.16.0.1/24
    ip dhcp-server pool-name dhcpv4-home-office
end
```

### Explanation:

- Creates an IPv4 DHCP pool for the subnet `172.16.0.0/24`.
- Defines a pool of addresses from `172.16.0.50` to `172.16.60.254`.
- Specifies the default gateway (`option routers`) as `172.16.0.1`.
- Associates the DHCP pool with the Gig0 interface.

## IPv6

```shell
clear router-db
yes


configure terminal

dhcp dhcpv6-home-office
    subnet fd00:abcd:1234::0/64
    pool fd00:abcd:1234::100 fd00:abcd:1234::1ff /64
    mode slaac
end

interface Gig0
    ip address fd00:abcd:1234::1/64
    ip dhcp-server pool-name dhcpv6-home-office
end
```

### Explanation:

- Creates an IPv6 DHCP pool for the subnet `fd00:abcd:1234::0/64`.
- Defines a pool of addresses from `fd00:abcd:1234::100` to `fd00:abcd:1234::1ff`.
- Associates the DHCP pool with the Gig0 interface.

## Dual-Stack

```shell
cls
configure terminal

dhcp dhcpv4-home-office
    subnet 172.16.0.0/24
    pool 172.16.0.50 172.16.60.254 255.255.255.0
    option routers 172.16.0.1
end

dhcp dhcpv6-home-office
    subnet fd00:abcd:1234::0\64
    pool fd00:abcd:1234::100 fd00:abcd:1234::1ff \64
    option routers fd00:abcd:1234::1
end

interface Gig0
    ip address 172.16.0.1/24
    ip address fd00:abcd:1234::1/64 secondary
    ip dhcp-server pool dhcpv4-home-office
    ip dhcp-server pool dhcpv6-home-office
end

```

### Explanation:

- Configures both IPv4 and IPv6 DHCP pools.
- Associates both DHCP pools with the Gig0 interface.
- Enables dual-stack support on the Gig0 interface.

## Multiple Interfaces

```shell
cls
configure terminal

; Create DHCP Pools
dhcp dhcpv4-home-office-1
    subnet 172.16.0.0/24
    pool 172.16.0.50 172.16.60.254 255.255.255.0
    pool 172.16.0.70 172.16.80.254 255.255.255.0
    reservations hw-address 0000.aaaa.0002 ip-address 172.16.0.2
    reservations hw-address 0000.aaaa.0003 ip-address 172.16.0.3 
    option routers 172.16.0.1
end

dhcp dhcpv4-home-office-2
    subnet 172.16.1.0/24
    pool 172.16.1.50 172.16.1.254 255.255.255.0
    option routers 172.16.1.1
end

; Apply DHCP Pool to Interface
interface Gig0
    ip address 172.16.0.1/24
    ip dhcp-server pool-name dhcpv4-home-office-1
end

interface Gig1
    ip address 172.16.1.1/24
    ip dhcp-server pool-name dhcpv4-home-office-2
end
```

### Explanation:

- Configures multiple IPv4 DHCP pools for different subnets.
- Defines reservations based on hardware addresses.
- Associates each DHCP pool with its respective interface (Gig0 or Gig1).

