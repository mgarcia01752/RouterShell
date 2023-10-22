
# Bridge Configuration

## Introduction

Bridging is a network technology that allows you to connect multiple network segments and create a single logical network. This page provides instructions for configuring bridge settings on a network device.

## Prerequisites

Before configuring bridge settings, ensure you have the necessary information and access to your network device. You should also have a basic understanding of network bridging concepts.

## Enabling Bridge Configuration

To configure bridge settings on your network device, follow the steps below:

1. Access the device's command-line interface (CLI) by entering the following commands:

   ```shell
   enable
   configure terminal
   ```

   You will enter the configuration mode where you can make changes to the bridge settings.

### Bridge Configuration

A bridge allows you to connect network segments and create a single logical network. To configure a bridge, follow these steps:

1. Enter the bridge configuration mode by using the following command:

   ```shell
   bridge <bridge-name>
   ```

   - `<bridge-name>`: Replace this with the name of the bridge you want to configure.

2. Enable or disable the bridge by using the following command:

   ```shell
   [no] shutdown
   ```

   - `[no]`: Use the `no` prefix to disable the bridge if it's currently enabled.

3. Exit the bridge configuration mode when you are done:

   ```shell
   end
   ```

   This will return you to the global configuration mode.

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

   - `<bridge-name>`: Specify the name of the bridge group you want to add the interface to.

3. Enable the interface using the following command:

   ```shell
   no shutdown
   ```

4. Exit the interface configuration mode when you are done:

   ```shell
   end
   ```

   This will return you to the global configuration mode.

### Manual Linux interaction

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
    no shutdown
end

interface GigabitEthernet0
    bridge-group my-bridge
    no shutdown
end
```

In this example:

- We create a bridge named `my-bridge`.
- We disable the bridge initially using `[no] shutdown`.
- We add the GigabitEthernet0/1 interface to the bridge group.
- We enable the GigabitEthernet0/1 interface within the bridge group.

By following these steps, you can create a bridge configuration on your network device, allowing multiple network segments to be connected within a single logical network. Always be cautious when making changes to bridge settings, as misconfiguration can impact network connectivity.

## Cisco Reference

[Cisco IOS Bridge Commands](https://www.cisco.com/c/en/us/td/docs/ios/bridging/command/reference/br_book.pdf)

