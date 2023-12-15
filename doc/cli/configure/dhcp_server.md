# DHCP Server

## Phase I DNSMasq

## Phase II KEA

## Generic DHCP Server 2 Interface

```shell

cls
configure terminal


; Apply to all DHCP SERVER Configurations
dhcp global
    option time-servers 216.239.35.8
end

; Create DHCP Pools
dhcp dhcp-home-office-1
    subnet 172.16.0.0/24
    pool 172.16.0.50 172.16.60.254 255.255.255.0
    pool 172.16.0.70 172.16.80.254 255.255.255.0
    reservations hw-address 0000.aaaa.0002 ip-address 172.16.0.2
    reservations hw-address 0000.aaaa.0003 ip-address 172.16.0.3 
    option routers 172.16.0.1
end

dhcp dhcp-home-office-2
    subnet 172.16.1.0/24
    pool 172.16.1.50 172.16.1.254 255.255.255.0
    option routers 172.16.1.1
end

; Apply DHCP Pool to Interface
interface Gig0
    ip address 172.16.0.1/24
    ip dhcp-server pool-name dhcp-home-office-1
end

interface Gig1
    ip address 172.16.1.1/24
    ip dhcp-server pool-name dhcp-home-office-2
end

```