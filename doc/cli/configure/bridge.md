# Bridge Configuration

## Introduction

Bridging is a network technology that connects multiple network segments, creating a single logical network. This document provides instructions for configuring bridge settings on a network device.

## Prerequisites

Before configuring bridge settings, ensure you have the necessary information and access to your network device. You should also have a basic understanding of network bridging concepts.

## Enabling Bridge Configuration

To configure bridge settings on your network device, follow these steps:

1. Access the device's command-line interface (CLI) by entering the following commands:

   ```shell
   enable
   configure terminal
   ```

   This will put you in configuration mode, where you can make changes to the bridge settings.

### Bridge Configuration

A bridge allows you to connect network segments and create a single logical network. To configure a bridge, follow these steps:

1. Enter the bridge configuration mode by using the following command:

   ```shell
   bridge <bridge-name>
   ```

   - `<bridge-name>`: Replace this with the name of the bridge you want to configure.

2. Set the management IP address (Requirement):

   ```shell
   management-inet <ip-address>
   ```

   - `<ip-address>`: Replace this with the management IP address for the bridge.

3. Enable or disable the bridge by using the following command:

   ```shell
   [no] shutdown
   ```

   - `[no]`: Use the `no` prefix to enable the bridge. Omitting `no` will disable the bridge.

4. Optionally, set the Spanning Tree Protocol (STP) state:

   ```shell
   stp <enable|disable>
   ```

   - `enable`: Enable STP.
   - `disable`: Disable STP.

5. Optionally, set the bridge protocol:

   ```shell
   protocol <IEEE_802_1D|IEEE_802_1W|IEEE_802_1S>
   ```

   - `IEEE_802_1D`: Standard STP.
   - `IEEE_802_1W`: Rapid STP (currently not supported).
   - `IEEE_802_1S`: Multiple STP (currently not supported).

6. Exit the bridge configuration mode when you are done:

   ```shell
   end
   ```

   This returns you to the global configuration mode.

### Interface Configuration

To add an interface to a bridge group, follow these steps:

1. Enter the interface configuration mode for the desired interface:

   ```shell
   interface <interface-name>
   ```

   - `<interface-name>`: Replace this with the name of the network interface you want to configure.

2. Add the interface to a bridge group using the following command:

   ```shell
   bridge-group <bridge-name>
   ```

   - `<bridge-name>`: Specify the name of the bridge group to add the interface to.

3. Enable the interface using the following command:

   ```shell
   no shutdown
   ```

4. Exit the interface configuration mode when you are done:

   ```shell
   end
   ```

   This returns you to the global configuration mode.

### Manual Linux Interaction

To manually interact with Linux bridges:

```shell
enable
configure terminal

show interfaces
shell sudo ip link delete brX type bridge
```

### Example: Bridge Configuration

Here's an example of configuring a bridge on a network device:

```shell
enable
configure terminal

bridge my-bridge
   management-inet 192.168.0.1
   no shutdown
end

interface eth0
    bridge-group my-bridge
    no shutdown
end
```

In this example:

- We create a bridge named `my-bridge`.
- We set the management IP address to `192.168.0.1`.
- We enable the bridge using `no shutdown`.
- We add the `eth0` interface to the bridge group.
- We enable the `eth0` interface within the bridge group.

By following these steps, you can create a bridge configuration on your network device, allowing multiple network segments to be connected within a single logical network. Always be cautious when making changes to bridge settings, as misconfiguration can impact network connectivity.

