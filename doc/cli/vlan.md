
# VLAN Configuration

## Introduction

VLANs (Virtual LANs) are a fundamental network segmentation technology that allows you to logically divide a network into separate broadcast domains. This page provides instructions for configuring VLANs and assigning them to network interfaces on a network device.

## Prerequisites

Before configuring VLANs, ensure you have the necessary information and access to your network device. You should also have a basic understanding of VLAN concepts.

## Enabling VLAN Configuration

To configure VLANs and assign them to network interfaces on your network device, follow the steps below:

1. Access the device's command-line interface (CLI) by entering the following commands:

   ```config
   enable
   configure terminal
   ```

   You will enter the configuration mode where you can make changes to VLAN settings.

### VLAN Configuration

A VLAN allows you to logically segment a network. To configure a VLAN, follow these steps:


1. Enter the VLAN configuration mode by using the following command:

   ```config
   vlan <vlan-id>
   ```

   - `<vlan-id>`: Replace this with the desired VLAN ID.

2. Provide a name for the VLAN using the following command:

   ```config
   name <vlan-name>
   ```

   - `<vlan-name>`: Specify the name for the VLAN.

3. Exit the VLAN configuration mode when you are done:

   ```
   end
   ```

   This will return you to the global configuration mode.

### Interface Assignment to VLAN

After configuring a VLAN, you can assign it to a network interface. To do this, follow these steps:

1. Enter the interface configuration mode for the desired interface by using the following command:

   ```config
   interface <interface-name>
   ```

   - `<interface-name>`: Replace this with the name of the network interface you want to assign to the VLAN.

2. Configure the interface as an access port and specify the VLAN using the following command:

   ```config
   switchport access vlan <vlan-name>
   ```

   - `<vlan-name>`: Specify the name of the VLAN you want to assign to the interface.

3. Exit the interface configuration mode when you are done:

   ```config
   end
   ```

   This will return you to the global configuration mode.

### Basic VLAN Configuration Example

```config
enable
configure terminal

vlan 1000
   name Vlan1000
   description "Office Vlan"
   end

rename if enx9cebe81be18a if-alias Gig0

interface Gig0
   switchport mode access vlan 1000
   end
```

### Conclusion

Configuring VLANs and assigning them to network interfaces is essential for network segmentation and managing network traffic effectively. By following the steps outlined in this guide, you can create VLANs and associate them with specific interfaces on your network device. Always ensure that VLAN configurations align with your network requirements and design.