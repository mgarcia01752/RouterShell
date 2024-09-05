# Generic Router Encapsulation (GRE)

```shell

configure terminal

interface tunnel <tunnel-name>
 tunnel description
 [no] inet <[inet/32 | inet/124 | interface-name]>
 tunnel source <[interface | inet-address]>
 tunnel destination <inet-address>
 tunnel mode gre <point2point | multipoint>
 [no] [tunnel key < 0 - 4294967295 >]
 commit
end

```
