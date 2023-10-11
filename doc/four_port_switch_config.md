# Basic 4-Port Configuration

This basic configuration sets up a network with one egress gateway port (Gig0) and a LAN bridge (brlan0) that connects three ports (Gig1, Gig2, and Gig3). Additionally, it configures a loopback interface (loopback 0) with its IP address.

## Enabling Configuration Mode

1. Enter privileged EXEC mode by typing `enable`.

2. Enter global configuration mode with `configure terminal`.

## LAN Bridge Configuration

3. Create and configure a LAN bridge named "brlan0":

   ```config
   bridge brlan0
       no shutdown
   end
   ```
   This configures the LAN bridge and ensures it is active.

## Loopback Interface Configuration

4. Configure the loopback 0 interface with an IP address and associate it with the LAN bridge:

   ```config
   interface loopback 0
       ip address 10.10.10.1 255.255.255.0
       bridge group brlan0
       no shutdown
   end
   ```
   - The IP address `10.10.10.1` is assigned to the loopback interface.
   - The `bridge group brlan0` command associates the loopback with the LAN bridge.
   - The `no shutdown` command activates the loopback interface.

## GigabitEthernet 0 (Gig0) Configuration

5. Rename and configure GigabitEthernet 0 (Gig0):

   ```config
   flush enx3c8cf8f943a2
   rename if enx3c8cf8f943a2 if-alias Gig0

   interface Gig0
       ip address 172.16.0.1 255.255.255.0
       no shutdown
   end
   ```
   - The `flush` and `rename` commands change the alias of the interface for readability.
   - The `ip address` command assigns the IP address `172.16.0.1` to Gig0.
   - The `no shutdown` command activates Gig0.

## GigabitEthernet 1 (Gig1) Configuration

6. Rename and configure GigabitEthernet 1 (Gig1) and associate it with the LAN bridge:

   ```config
   flush enx00249b119cef
   rename if enx00249b119cef if-alias Gig1

   interface Gig1
       bridge group brlan0
       no shutdown
   end
   ```
   - The `flush` and `rename` commands change the alias of the interface for readability.
   - The `bridge group brlan0` command associates Gig1 with the LAN bridge.
   - The `no shutdown` command activates Gig1.

## GigabitEthernet 2 (Gig2) Configuration

7. Rename and configure GigabitEthernet 2 (Gig2) and associate it with the LAN bridge:

   ```config
   flush enx9cebe81be18a
   rename if enx9cebe81be18a if-alias Gig2

   interface Gig2
       bridge group brlan0
       no shutdown
   end
   ```
   - The `flush` and `rename` commands change the alias of the interface for readability.
   - The `bridge group brlan0` command associates Gig2 with the LAN bridge.
   - The `no shutdown` command activates Gig2.

## GigabitEthernet 3 (Gig3) Configuration

8. Rename and configure GigabitEthernet 3 (Gig3) and associate it with the LAN bridge:

    ```config

   flush enx8cae4cdb5f8e
   rename if enx8cae4cdb5f8e if-alias Gig3

   interface Gig3
       bridge group brlan0
       no shutdown
   end
   ```
   - The `flush` and `rename` commands change the alias of the interface for readability.
   - The `bridge group brlan0` command associates Gig3 with the LAN bridge.
   - The `no shutdown` command activates Gig3.

## Routing Configuration

9. Set up a static route to reach the 10.10.10.0 network through Gig0:

```config
   ```
   ip route 10.10.10.0 255.255.255.0 Gig0
   ```
   This static route directs traffic destined for the 10.10.10.0 network to use Gig0 as the gateway.

## Saving and Exiting Configuration

10. To save your configuration, use the `write memory` or `copy running-config startup-config` command.

11. Exit configuration mode with `exit`.

## Full Configuration

Here's the complete configuration for your reference:

```config
enable
configure terminal

bridge brlan0
    no shutdown
end

interface loopback 0
    ip address 10.10.10.1 255.255.255.0
    bridge group brlan0
    no shutdown
end

flush enx3c8cf8f943a2
rename if enx3c8cf8f943a2 if-alias Gig0

interface Gig0
    ip address 172.16.0.1 255.255.255.0
    no shutdown
end

flush enx00249b119cef
rename if enx00249b119cef if-alias Gig1

interface Gig1
    bridge group brlan0
    no shutdown
end

flush enx9cebe81be18a
rename if enx9cebe81be18a if-alias Gig2

interface Gig2
    bridge group brlan0
    no shutdown
end

flush enx8cae4cdb5f8e
rename if enx8cae4cdb5f8e if-alias Gig3

interface Gig3
    bridge group brlan0
    no shutdown
end

ip route 10.10.10.0 255.255.255.0 Gig0
```

This full configuration sets up a network with a bridge, loopback interface, and multiple GigabitEthernet ports with assigned IP addresses and routing. Feel free to modify it to suit your network requirements.
