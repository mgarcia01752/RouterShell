# Ethernet

```text
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
```


