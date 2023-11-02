# DNSMasq

## Router Configuration

```

configure terminal

dhcp dhcp-home-office-1
    subnet 172.16.1.0/24
    pool 172.16.1.50 172.16.1.60 255.255.255.0
    pool 172.16.1.70 172.16.1.80 255.255.255.0    
    reservations hw-address 0000.aaaa.0002 ip-address 172.16.1.2 
    reservations hw-address 0000.aaaa.0003 ip-address 172.16.1.3
    option routers 172.16.1.1
end

dhcp dhcp-home-office-2
    subnet 172.16.2.0/24
    pool 172.16.2.50 172.16.2.60 255.255.255.0
    pool 172.16.2.70 172.16.2.80 255.255.255.0    
    reservations hw-address 0000.bbbb.0002 ip-address 172.16.0.2 
    reservations hw-address 0000.cccc.0003 ip-address 172.16.0.3
    option routers 172.16.2.1
end

interface Gig0
    ip address 172.16.0.1/24
    ip dhcp-server pool dhcp-home-office-1
end

interface Gig1
    ip address 172.16.2.1/24
    ip dhcp-server pool dhcp-home-office-2
end

```


**Directory Tree:**

Let's assume you have a directory named `/etc/dnsmasq.d` where you'll place your individual configuration files. Your directory tree would look like this:

```
/etc/dnsmasq.d/
├── dhcp-home-office-1.conf
├── dhcp-home-office-2.conf
└── dnsmasq.conf
```

Now, I'll show you the content of each of these files.

**1. `dhcp-home-office-1.conf` (Configuration for DHCP Pool 1):**

`/etc/dnsmasq.d/dhcp-home-office-1.conf`:

```shell
# DHCP configuration for home office subnet 1 (172.16.1.0/24) on Gig0
# This file contains the settings specific to DHCP Pool 1

# Define the interface for DHCP Pool 1
interface=Gig0

# Define the DHCP range for Pool 1
dhcp-range=172.16.1.50,172.16.1.60,255.255.255.0
dhcp-range=172.16.1.70,172.16.1.80,255.255.255.0

# Define MAC address reservations for Pool 1
dhcp-host=00:00:aa:aa:00:02,172.16.1.2
dhcp-host=00:00:aa:aa:00:03,172.16.1.3

# Specify the default gateway for Pool 1
dhcp-option=3,172.16.1.1
```

**2. `dhcp-home-office-2.conf` (Configuration for DHCP Pool 2):**

`/etc/dnsmasq.d/dhcp-home-office-2.conf`:

```shell
# DHCP configuration for home office subnet 2 (172.16.2.0/24) on Gig1
# This file contains the settings specific to DHCP Pool 2

# Define the interface for DHCP Pool 2
interface=Gig1

# Define the DHCP range for Pool 2
dhcp-range=172.16.2.50,172.16.2.60,255.255.255.0
dhcp-range=172.16.2.70,172.16.2.80,255.255.255.0

# Define MAC address reservations for Pool 2
dhcp-host=00:00:bb:bb:00:02,172.16.2.2
dhcp-host=00:00:cc:cc:00:03,172.16.2.3

# Specify the default gateway for Pool 2
dhcp-option=3,172.16.2.1
```

**3. `dnsmasq.conf` (Main `dnsmasq` Configuration):**

`/etc/dnsmasq.conf`:

This file contains your main `dnsmasq` configuration, which might include global settings, DNS configuration, and other common settings. You can structure it as follows:

```shell
# Global settings
# Specify DNS server addresses
server=8.8.8.8
server=8.8.4.4

# Custom domain mapping
address=/mydomain.local/192.168.1.100
```

**Start `dnsmasq` with Separate Configuration Files:**

When you start the `dnsmasq` daemon, it will automatically load the main `dnsmasq.conf` file and any additional configuration files found in the `/etc/dnsmasq.d` directory. This way, you have organized your DHCP pool settings in separate files within the `dnsmasq.d` directory, and they will be applied as part of your `dnsmasq` configuration.

This approach makes it easier to manage and maintain different DHCP pools independently while keeping common global settings in the main `dnsmasq.conf` file.