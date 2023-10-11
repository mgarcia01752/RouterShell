# Configuring an Router for DHCP Server

This wiki provides a step-by-step guide on how to configure an IOS router to act as a DHCP server for your network. DHCP (Dynamic Host Configuration Protocol) simplifies the process of assigning IP addresses and providing network configuration information to clients. This guide assumes that you have already accessed the router's CLI (Command Line Interface).

## Enabling DHCP Global Configuration

1. **Enter Privileged Exec Mode**: Type `enable` and press Enter to access privileged exec mode.

2. **Enter Global Configuration Mode**: Type `configure terminal` and press Enter to enter global configuration mode.

3. **Access DHCP Global Configuration**:
   - Type `dhcp global` and press Enter to access DHCP global configuration.

4. **Configuring DHCP Options**:
   - To configure DHCP options, use the `option` command in the following format:

     ```
     option <dhcp-option> <[int | string | ip-address]>
     ```
   - Replace `<dhcp-option>` with the desired option name.
   - Specify the option type as `[int | string | ip-address]` as appropriate.
   - Repeat this command for each DHCP option you want to configure.

5. **Commit the Changes**: Type `commit` and press Enter to save the DHCP global configuration.

6. **Exit DHCP Global Configuration**: Type `end` and press Enter to exit the DHCP global configuration mode.

## Configuring a DHCP Pool

1. **Access DHCP Pool Configuration**:
   - Type `dhcp <dhcp-pool-name>` and press Enter to access DHCP pool configuration.
   - Replace `<dhcp-pool-name>` with the name you want to assign to the DHCP pool.

2. **Defining the Subnet**:
   - Use the `subnet` command to define the IP subnet and mask in the following format:

     ```
     subnet <ip-subnet>/<mask>
     ```
   - Replace `<ip-subnet>` with the subnet address and `<mask>` with the subnet mask.

3. **Configuring IP Address Pool Range**:
   - Use the `pool` command to specify the IP address range for the pool in the following format:
     ```
     pool <ip-address-start> <ip-address-end>
     ```
   - Replace `<ip-address-start>` with the first IP address in the pool range, and `<ip-address-end>` with the last IP address.

4. **Creating Reservations**:
   - You can create reservations for specific clients using the `reservations` command in the following format:
     ```
     reservations [hw-address | duid] <mac-address> ip-address <ip-address> [hostname <string>]
     ```
   - Choose between `hw-address` or `duid` to identify the client.
   - Provide the client's MAC address, IP address, and an optional hostname.

5. **Configuring Additional Options**:
   - To configure additional DHCP options for the pool, use the `option` command as shown earlier.

6. **Commit the Changes**: Type `commit` and press Enter to save the DHCP pool configuration.

7. **Exit DHCP Pool Configuration**: Type `end` and press Enter to exit the DHCP pool configuration mode.

## Associating DHCP Pool with an Interface

1. **Access Interface Configuration**:
   - Type `interface <interface-name>` and press Enter to access the configuration of the specific interface you want to associate with the DHCP pool.
   - Replace `<interface-name>` with the name of the interface (e.g., GigabitEthernet0/0).

2. **Associating with DHCP Pool**:
   - To enable DHCP for the interface and associate it with a DHCP pool, use the following command:
     ```
     dhcp-server pool-name <dhcp-pool-name>
     ```
   - Replace `<dhcp-pool-name>` with the name of the DHCP pool you configured earlier.

3. **Exit Interface Configuration**: Type `end` and press Enter to exit the interface configuration mode.

Your router is now configured as a DHCP server. It will assign IP addresses and provide network configuration information to clients associated with the specified DHCP pool. Make sure to save your configuration changes if necessary to ensure they persist across router restarts.

For specific configuration details and available DHCP options, refer to your router's documentation and consult the documentation.

```
enable
configure terminal

dhcp global
    option <dhcp-option> <[int | string | ip-address]>
    commit
    end    

dhcp <dhcp-pool-name>
    subnet <ip-subnet>/<mask>
    pool <ip-address-start> <ip-address-start>
    reservations [hw-address | duid] <mac-address> ip-address <ip-address> [hostname <string>]
    [option <option-name> <[int | string | ip-address]>]
    commit
    end        

interface <interface-name>
    [no] dhcp-server pool-name <dhcp-pool-name>
    end
```

## Kea DHCP [KEA Website](https://www.isc.org/kea/)

```json
{
    "Dhcp4": {
        "valid-lifetime": 4000,
        "renew-timer": 1000,
        "rebind-timer": 2000,
        "interfaces-config": {
            "interfaces": [
                "eth0"
            ],
            "service-sockets-max-retries": 5,
            "service-sockets-retry-wait-time": 5000
        },
        "lease-database": {
            "type": "memfile",
            "persist": true,
            "name": "/var/lib/kea/dhcp4.leases"
        },
        "subnet4": [
            {
                "interface": "eth0",
                "subnet": "192.0.2.1/24",
                "pools": [
                    {
                        "pool": "192.0.2.10 - 192.0.2.20",
                        "option-data": [
                            {
                                "time-offset": 10000,
                                "routers": "192.0.2.1",
                                "time-servers": "192.0.2.3",
                                "name-servers": "192.0.2.3",
                                "domain-name-servers": "192.0.2.3",
                                "log-servers": "192.0.2.3",
                                "domain-name": "192.0.2.1",
                                "ntp-servers": "192.0.2.1",
                                "boot-file-name": "192.0.2.1",
                                "smtp-server": "192.0.2.1",
                                "pop-server": "192.0.2.1",
                                "nntp-server": "192.0.2.1",
                                "www-server": "192.0.2.1"
                            }
                        ]
                    }
                ],
                "reservations": [
                    {
                        "hw-address": "1a:1b:1c:1d:1e:1f",
                        "ip-address": "192.0.2.100",
                        "hostname": ""
                    },
                    {
                        "duid": "0a:0b:0c:0d:0e:0f",
                        "ip-address": "192.0.2.101",
                        "hostname": ""
                    }
                ]
            }
        ]
    }
}

```