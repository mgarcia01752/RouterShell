# Loopback

## General Loopback Configuration

```plaintext
   interface loopback<id>
      description <Description of loopback>
      [no] [mac [auto | <mac-address>]]
      [no] [ip address <ip-address>/<CIDR> [secondary]]
      [no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]
      [no] shutdown
      destroy YES
   end
```

### Command Descriptions

- **interface loopback<id>**: 
  - This command is used to create or modify a loopback interface. Replace `<id>` with the loopback interface number (e.g., `loopback0`).

- **description <Description of loopback>**:
  - Adds a text description to the loopback interface. Useful for documentation and identifying the purpose of the interface.
  - Example: `description Management Loopback`

- **[no] [mac [auto | <mac-address>]]**:
  
  - Configures the MAC address for the loopback interface.
  - `auto` sets the MAC address automatically.
  - `<mac-address>` allows specifying a custom MAC address.
  - `no mac` removes the MAC address configuration.
  - Example: `mac 00:11:22:33:44:55` or `no mac auto`

- **[no] [ip address <ip-address>/<CIDR> [secondary]]**:
  
  - Assigns an IPv4 address to the loopback interface.
  - `<ip-address>/<CIDR>` specifies the IP address and subnet mask.
  - `secondary` allows adding a secondary IP address.
  - `no ip address` removes the IP address.
  - Example: `ip address 192.168.1.1/24` or `ip address 192.168.1.2/24 secondary`

- **[no] [ipv6 address <ipv6-ip-address>/<CIDR> [secondary]]**:
  
  - Assigns an IPv6 address to the loopback interface.
  - `<ipv6-ip-address>/<CIDR>` specifies the IPv6 address and prefix length.
  - `secondary` allows adding a secondary IPv6 address.
  - `no ipv6 address` removes the IPv6 address.
  - Example: `ipv6 address 2001:db8::1/64` or `ipv6 address 2001:db8::2/64 secondary`

- **[no] shutdown**:
  
  - Disables the loopback interface.
  - `no shutdown` enables the interface.
  - Example: `shutdown` or `no shutdown`

- **destroy**:
  
  - Deletes the loopback interface.
  - Example: `destroy`

### Example Configuration

Below is an example of configuring a loopback interface:

```plaintext
interface loopback0
   description Management Loopback
   mac 00:11:22:33:44:55
   ip address 192.168.1.1/24
   ipv6 address 2001:db8::1/64
   no shutdown
end
```

In this example:

- A loopback interface `loopback0` is created.
- A description "Management Loopback" is added.
- The MAC address is set to `00:11:22:33:44:55`.
- The IPv4 address is set to `192.168.1.1/24`.
- The IPv6 address is set to `2001:db8::1/64`.
- The interface is enabled with `no shutdown`.

### Removing Configuration

To remove the configuration or the loopback interface, use the following commands:

```plaintext
interface loopback0
   destroy YES
end
```
