# Remaining Support Systems

## DHCP

### DHCPv4 Support

config global and interface (Complete)
show dhcp commands

### DHCPv6 Support

### Upload KEA Dhcp.conf

### KEA Server Start/Stop


## Wireless

### Wireless Global Config

### Show Commands

show linux-cmd
show sysctl-cmd
show log

## Routing Protocols

### RIP

### OSPF

### Auto Generate Configuration based on local network settings

```shell
    # Based on OS network
    show os configuration

    # Based on RouterShell running/start-up network
    show running configuration
    show start configuration

```

### BGP

## System Commands

### copy run-config startup-config or write memory

### Global USER commands

cls - clear screen
quit = end = exit

tree | grep -v -e '__pycache__' -e '\.pyc$'

### Testing Config

cls

flush Gig0
flush Gig1

configure terminal

ip nat pool home-nat

bridge brlan0
    no shutdown
end

bridge brlan1
    no shutdown
end

interface Gig0
    ip address 172.16.0.1/24
    ip nat outside pool home-nat
    bridge group brlan0
    no shutdown
end

interface Gig1
    ip address 172.16.1.1/24
    ip nat inside pool home-nat
    bridge group brlan1
    no shutdown
end