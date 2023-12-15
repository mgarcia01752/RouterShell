# Global Priv Exec Commands

This page provides information about global Priv Exec commands that allow users with administrative privileges to perform various system-level tasks.

## hostname

```shell
configure terminal
hostname local-hostname
```

## banner (Message of the Day)

```shell
configure terminal
banner motd ^
BANNER MESSAGE OF THE DAY
^
```
## Negate banner (Message of the Day)

```shell
configure terminal
no banner motd 
```

## banner (Login)

```shell
configure terminal
banner login ^
BANNER LOGIN MESSAGE
^
```

## Negate banner (Login)

```shell
configure terminal
no banner login
```

## flush

The `flush` command is used to clear or reset specific system components or settings. It can be used to clear interfaces, NAT translations, VLAN information, routing tables, and more.

### Syntax

```shell
enable
flush [interface | nat | vlan | route] [<name>]
```

- `enable`: Enter Privileged Exec mode.
- `flush`: Initiates the flush operation.
- `[interface | nat | vlan | route]`: Specify the type of information to flush (e.g., interfaces, NAT translations, VLANs, routing tables).
- `<name>`: Optionally, provide a specific name or identifier to target a particular instance.

## reboot

The `reboot` command is used to restart the network device, initiating a system reboot.

### Syntax

```shell
enable
reboot
```

- `reboot`: Initiates a system reboot. Use this command with caution, as it will result in a temporary loss of network connectivity.

## Add/Delete User

The `Add/Delete User` commands are used to create or remove user accounts with administrative privileges. Users are assigned a user name, privilege level, and an optional duration for which their account remains active.

### Syntax

```shell
enable
configure terminal
[no] username <user-name> level <user-level (1-5)> [duration <time-in-seconds-stay-active>]
```

- `enable`: Enter Privileged Exec mode.
- `configure terminal`: Enter Global Configuration mode.
- `[no] username <user-name>`: Create or delete a user account, specifying the user's name.
- `level <user-level (1-5)>`: Assign a privilege level to the user (ranging from 1 to 5, with 5 being the highest).
- `[duration <time-in-seconds-stay-active>]`: Optionally, specify a duration for which the user's account will remain active.


## Configuration Commands

### Rename Interface Alias

The `rename if <interface> if-alias <interface-alias>` command allows you to rename a network interface alias.

```shell
enable
configure terminal
rename if <interface> if-alias <interface-alias>
```

- `configure terminal`: Enter Global Configuration mode.
- `rename if <interface>`: Specify the name of the network interface you want to rename.
- `if-alias <interface-alias>`: Specify the new alias for the network interface.

These configuration commands are valuable for managing network devices and optimizing network performance. Use them with caution, as they can impact network operation.

## Clear Commands

The "Clear Commands" section includes various commands to clear specific networking components or statistics. Here are some examples:

### clear arp-cache

The `clear arp-cache` command is used to clear the ARP (Address Resolution Protocol) cache, removing ARP entries.

```shell
enable
clear arp-cache
```

### clear ip nat translation

The `clear ip nat translation` command is used to clear Network Address Translation (NAT) translations.

```shell
enable
clear ip nat translation
```

### clear access-list counters

The `clear access-list counters` command is used to clear packet and byte counters for a specific access control list (ACL).

```shell
enable
clear access-list counters <acl-name>
```

These "Clear Commands" are valuable for maintaining network performance and troubleshooting network issues. Use them with caution, as they can impact network operation.