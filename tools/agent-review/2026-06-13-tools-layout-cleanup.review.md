### Summary
Grouped formerly flat tools by purpose so destructive disk, network, and service helpers are easier to identify before use. Updated tool documentation and quality gates, made the dnsmasq example stdout-first, and cleaned touched Python helpers for validation.

### Modified Files
- README.md
- tools/dev/clear-pycache.sh
- tools/dev/clear-routershell-db.sh
- tools/disk/check_drive.sh
- tools/disk/create-ext4-bootable.sh
- tools/disk/create_ubuntu_install.sh
- tools/disk/format_drive.sh
- tools/examples/gen_dnsmasq_config.py
- tools/git/README.md
- tools/git/git-common.sh
- tools/hardware/cpu_hw_summary.py
- tools/hardware/network_hw_detection.py
- tools/hardware/usb_to_ethernet_find.sh
- tools/network/bridge_control_options.sh
- tools/network/configure_nat.sh
- tools/network/create_complete_network.sh
- tools/network/reset_network.sh
- tools/network/toggle_interface_state.sh
- tools/network/vlan_create.sh
- tools/network/vlan_destroy.sh
- tools/network/vlan_show.sh
- tools/network/wlan_access_point.sh
- tools/reference/tools-layout.md
- tools/reference/wi.txt
- tools/release/test-runner.py
- tools/services/dhcp_client_simulation.sh
- tools/services/dhcp_server_options.sh
- tools/services/uninstall_dnsmasq.sh
- tools/services/uninstall_kea_server.sh

### Commands Executed And Results
- `python3 -m py_compile routershell/__init__.py routershell/__main__.py routershell/_version.py routershell/cli.py tests/packaging/test_entry_points.py tests/packaging/test_imports.py tests/packaging/test_version.py tools/examples/gen_dnsmasq_config.py tools/hardware/cpu_hw_summary.py tools/hardware/network_hw_detection.py tools/release/check_version.py tools/release/release.py tools/release/test-runner.py tools/support/bump_version.py` -> pass
- `find start.sh install tools -path "tools/agent-review" -prune -o -name "*.sh" -exec bash -n {} \;` -> pass
- `/tmp/routershell-root-clean-check/bin/python -m pytest` -> pass, 4 tests
- `/tmp/routershell-root-clean-check/bin/python -m ruff check routershell tests/packaging tools/examples tools/hardware tools/release tools/support` -> pass
- `/tmp/routershell-root-clean-check/bin/python -m build` -> pass, sdist and wheel built
- `bash -c 'source tools/git/git-common.sh; rs_run_quality_gates'` -> pass available gates; pytest and ruff skipped for system Python because they are not installed there

### Tests
- `pytest` -> pass, 4 tests
- `ruff` -> pass for RouterShell package, packaging tests, and touched tool Python paths
- `build` -> pass through the project test virtual environment

### Notes / Warnings
- Disk, network, and service tools remain host-mutating utilities; run them in disposable VMs unless the host change is intentional.
- System Python does not have `build`, `pytest`, or `ruff`; venv validation was used for those commands.

### Remaining TODOs / Follow-Ups
- None

# FILE: README.md
# RouterShell (WORK IN PROGRESS)

RouterShell is an open-source, IOS-like CLI distribution written in Python 3. It is designed to provide a flexible and user-friendly command-line interface for network administrators and enthusiasts, offering a comprehensive range of networking features and capabilities tailored to diverse needs.

**Key Features of RouterShell:**

1. **Interface Configurations:** RouterShell supports a variety of interface configurations, including:
   - **Loopback Interfaces:** Ideal for testing and diagnostics, loopback interfaces are easy to set up and provide a versatile tool for network validation.
   - **Physical Interfaces:** Compatibility with Ethernet, USB, wireless (WiFi and cellular) interfaces, making it adaptable to various hardware environments.
   - **Bridging:** Enables the connection of different network segments, which is beneficial in creating complex network topologies.
   - **VLAN Support:** Facilitates network segmentation and organization, which is crucial for larger, more intricate networks.

2. **Tunneling:** RouterShell includes support for tunneling protocols, such as GRE (Generic Routing Encapsulation), allowing the creation of point-to-point and point-to-multipoint tunnels. This feature enables the encapsulation of packets for secure and efficient transport across different network segments, which is useful in VPNs and cross-network communication.

3. **NAT (Network Address Translation) Support:** Provides NAT functionality, essential for translating private IP addresses to public IP addresses, commonly required in both home and enterprise network setups. This feature helps in conserving public IP addresses and adds a layer of security by masking internal network structures.

4. **Access Control List (ACL) and Firewall Support:** RouterShell supports ACLs and firewall functionalities, offering enhanced network security by controlling incoming and outgoing traffic based on predefined rules. This is crucial for protecting network resources and managing data flow effectively.

RouterShell aims to provide a comprehensive CLI experience similar to traditional network operating systems, with the flexibility and extensibility of Python, making it a valuable tool for managing and automating network environments.


Regarding its intended use:

- **Quick Router Deployment:** RouterShell is designed to expedite router setup using a minimal Linux image, a valuable feature when rapid deployment is crucial.

- **Router-on-a-Stick Configuration:** RouterShell supports the "router-on-a-stick" configuration, useful for scenarios requiring network segmentation.

- **Compatibility with Embedded Router Distributions:** While initially developed with a focus on Ubuntu, RouterShell's lower layers are designed to be OS-agnostic, potentially allowing compatibility with various lightweight Linux distributions.

In conclusion, RouterShell is a router CLI distribution with features well-suited for specific network setups and security requirements. However, it is crucial to thoroughly assess your specific networking needs and consider whether RouterShell aligns with them before selecting it as your networking solution. Its comprehensive feature set, including NAT support and access control list/firewall support, makes it a versatile choice for network administrators and enthusiasts looking to configure and manage network infrastructure efficiently.

## Table of Contents

- [Global Privileged EXEC Commands](doc/cli/global_priv_exec_cmd.md): Learn about global privileged EXEC commands for system-level tasks.

- [ARP (Address Resolution Protocol)](doc/cli/configure/arp.md): Understand ARP and how it works in RouterShell.

- [Bridge Configuration](doc/cli/configure/bridge.md): Configure and manage bridges in RouterShell.

- [DHCPv4/v6 Configuration](doc/cli/configure/dhcp.md): Explore DHCP (Dynamic Host Configuration Protocol) setup for IPv4 and IPv6.

- [Interface Configuration](doc/cli/configure/config.md): Configure and manage network interfaces in RouterShell.

- [NAT (Network Address Translation)](doc/cli/configure/nat.md): Set up Network Address Translation for your RouterShell router.

- [Route Configuration](doc/cli//configureroute.md): Understand the routing and how to configure it in RouterShell.

- [VLAN Configuration](doc/cli//configurevlan.md): Configure and manage VLANs in your RouterShell network.

- [System Configuration](doc/cli/global/system.md): Learn about system-level configuration options in RouterShell.

- [Wireless Configuration](doc/cli/configure/wireless.md): Explore wireless network configuration in RouterShell.

## Router Configuration Examples

Explore a variety of router configuration examples to help you get started with RouterShell:

These examples cover scenarios like configuring a four-port bridge with VLAN support, setting up a four-port switch, and configuring NAT for a two-port setup. You can access the detailed instructions and information in the respective configuration files.

- [Four-Port Bridge with VLAN Configuration](doc/cli/four_port_bridge_vlan_config.md): This example guides you through setting up a four-port bridge with VLAN support, allowing for network segmentation and efficient traffic management.

- [Four-Port Switch Configuration](doc/cli/four_port_switch_config.md): Learn how to configure a four-port switch, which is essential for creating a network with multiple connected devices.

- [Two-Port NAT Configuration](doc/cli/two_port_nat_config.md): Understand how to set up Network Address Translation (NAT) for a two-port router, enabling the translation of private IP addresses to public IP addresses.

These configuration examples serve as practical guides to help you implement specific networking setups with RouterShell. Refer to the linked documentation files for step-by-step instructions and detailed explanations.

Feel free to explore these examples and adapt them to your networking needs. If you have any questions or need further assistance, don't hesitate to contact our community or project team. Thank you for choosing RouterShell!

## Additional Resources

Please select the specific documentation file you are interested in from the table of contents above to access detailed information and instructions for configuring and using RouterShell.

If you have any questions or need further assistance, please feel free to reach out to our community or project team. Thank you for choosing RouterShell!

- [RouterShell FAQ](doc/faq.md)

## Linux Runtime Install

[README INSTALLATION](install/README.md)

RouterShell includes a generic installer for non-embedded Linux hosts such as
Ubuntu, Debian, Fedora, RHEL-compatible systems, and openSUSE. Embedded and
BusyBox-style targets are intentionally out of scope for this installer.

Production install is the default.
The installer captures a root-only baseline snapshot under
`/var/lib/routershell/baseline` before making install changes.

Test installer changes in a disposable VM before running them on a development
workstation. Use `--development` only when testing editable installs with dev
dependencies; see [RouterShell VM Install Testing](tools/vm/README.md).

```bash
sudo ./install/install.sh
routershell
```

## Run RouterShell From Source

```bash
python3 -m routershell
```

Run the factory reset workflow from source with:

```bash
python3 -m routershell --factory-reset
```

## Python Development Install

RouterShell now includes Python packaging metadata in `pyproject.toml`.
For local development, use an isolated virtual environment and install the
project in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

After installation, run the CLI entry point:

```bash
routershell
```

Factory reset is also exposed as a console entry point:

```bash
routershell-factory-reset
```

Build distribution artifacts with:

```bash
python -m build
```

Run validation with:

```bash
python -m pytest
python -m ruff check .
```

## Git Helpers

Git helper scripts live under `tools/git/`:

```bash
./tools/git/git-save.sh --commit-msg "Update RouterShell"
./tools/git/git-push.sh --commit-msg "Update RouterShell"
```

See [RouterShell Git Helpers](tools/git/README.md) for save, push, and guarded branch
history reset workflows.

## Tools

Operational and development tools are grouped under `tools/` by purpose.
Review [RouterShell Tools Layout](tools/reference/tools-layout.md) before
running scripts that can alter disks, networking, packages, or services.

## Release Helpers

Release helper scripts live under `tools/release/`:

```bash
./tools/release/check_version.py
./tools/release/release.py --next patch --dry-run
```

See [RouterShell Release Helpers](tools/release/README.md) for version checks,
dry runs, releases, and commit reports.

## [TODO](todo.md)

# FILE: tools/dev/clear-pycache.sh
#!/usr/bin/env bash

# Function to clear __pycache__ directories recursively
clear_pycache() {
    local dir_path="$1"

    # Find and delete all __pycache__ directories
    find "$dir_path" -type d -name "__pycache__" -exec rm -r {} +

    echo "All __pycache__ directories have been deleted from $dir_path."
}

# Check if the directory path is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/your/directory"
    exit 1
fi

# Call the function with the provided directory path
clear_pycache "$1"

# FILE: tools/dev/clear-routershell-db.sh
#!/usr/bin/env bash

# Prompt the user for confirmation
read -p "Are you sure you want to delete the router-shell db file (routershell.db)? (Y|y/n) " -n 1 -r
echo

# Check if the user's response is Y or y
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Find the routershell.db file in the relative path
    db_files=$(find . -type f -name "routershell.db")

    # Check if there is exactly one db file found
    if [ $(echo "$db_files" | wc -l) -eq 1 ]
    then
        echo "Deleting the file..."
        rm "$db_files"
    elif [ -z "$db_files" ]
    then
        echo "No routershell.db file found."
    else
        echo "Multiple routershell.db files found. Please ensure there is only one file."
    fi
else
    echo "Operation cancelled."
fi

# FILE: tools/disk/check_drive.sh
#!/usr/bin/env bash

while getopts ":d:" opt; do
  case $opt in
    d)
      drive="/dev/$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG. Specify the drive using -d (e.g., -d sda)"
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument. Specify the drive using -d (e.g., -d sda)"
      exit 1
      ;;
  esac
done

if [ -z "$drive" ]; then
  echo "Please specify the drive using -d (e.g., -d sda)"
  exit 1
fi

# Check and repair file system using fsck
echo "Checking and repairing file system for $drive..."
sudo fsck "$drive"

# Check SMART status
echo "Checking SMART status for $drive..."
sudo smartctl -a "$drive"

# Additional commands or checks can be added as needed

echo "Script completed."

# FILE: tools/disk/create-ext4-bootable.sh
#!/usr/bin/env bash

set -e

# Function to display usage
usage() {
    echo "Usage: $0 -d <device> -p <partition> -h <hostname> -t <target> -b <bootloader> -v <distro_version>"
    echo "  -d <device>         : Target device (e.g., /dev/sdX)"
    echo "  -p <partition>      : Target partition (e.g., /dev/sdXn)"
    echo "  -h <hostname>       : Hostname for the new system"
    echo "  -t <target>         : Mount point for the target system (e.g., /mnt/target)"
    echo "  -b <bootloader>     : Bootloader type (grub-pc or grub-efi)"
    echo "  -v <distro_version> : Distribution version (e.g., stable for Debian)"
    exit 1
}

# Function to check if the device and partition exist
check_device_partition() {
    if [ ! -b "$1" ]; then
        echo "Error: Device $1 does not exist."
        exit 1
    fi

    if [ ! -b "$2" ]; then
        echo "Error: Partition $2 does not exist."
        exit 1
    fi
}

# Function to check if the partition is mounted
check_mounted() {
    if mount | grep "$1" > /dev/null; then
        echo "Error: Partition $1 is mounted. Please unmount it before proceeding."
        exit 1
    fi
}

# Function to confirm user choices
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting."
        exit 1
    fi
}

# Parse command-line arguments
while getopts ":d:p:h:t:b:v:" opt; do
    case "${opt}" in
        d)
            DEVICE=${OPTARG}
            ;;
        p)
            PARTITION=${OPTARG}
            ;;
        h)
            HOSTNAME=${OPTARG}
            ;;
        t)
            TARGET=${OPTARG}
            ;;
        b)
            BOOTLOADER=${OPTARG}
            ;;
        v)
            DISTRO_VERSION=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

# Check if all arguments are provided
if [ -z "${DEVICE}" ] || [ -z "${PARTITION}" ] || [ -z "${HOSTNAME}" ] || [ -z "${TARGET}" ] || [ -z "${BOOTLOADER}" ] || [ -z "${DISTRO_VERSION}" ]; then
    usage
fi

# Ensure the user really wants to format and use the specified device
echo "WARNING: This script will format the partition ${PARTITION} on device ${DEVICE}."
confirm "Do you want to continue?"

# Check if device and partition exist
check_device_partition "${DEVICE}" "${PARTITION}"

# Check if partition is mounted
check_mounted "${PARTITION}"

# Format the partition
echo "Formatting partition ${PARTITION} as ext4..."
sudo mkfs.ext4 "${PARTITION}"

# Mount the partition
echo "Mounting partition ${PARTITION} to ${TARGET}..."
sudo mkdir -p "${TARGET}"
sudo mount "${PARTITION}" "${TARGET}"

# Install base system using debootstrap (Debian)
echo "Installing base system..."
sudo debootstrap "${DISTRO_VERSION}" "${TARGET}" http://deb.debian.org/debian/

# Chroot into the new system
echo "Configuring the new system..."
sudo mount --bind /dev "${TARGET}/dev"
sudo mount --bind /proc "${TARGET}/proc"
sudo mount --bind /sys "${TARGET}/sys"
sudo chroot "${TARGET}" /bin/bash <<EOF
set -e
echo "${HOSTNAME}" > /etc/hostname
genfstab -U / > /etc/fstab
echo "root:root" | chpasswd
EOF

# Install and configure the bootloader
echo "Installing and configuring the bootloader..."
if [ "$BOOTLOADER" == "grub-pc" ]; then
    sudo chroot "${TARGET}" /bin/bash <<EOF
apt-get update
apt-get install -y grub-pc linux-image-amd64
grub-install --target=i386-pc --recheck "${DEVICE}"
update-grub
EOF
elif [ "$BOOTLOADER" == "grub-efi" ]; then
    sudo chroot "${TARGET}" /bin/bash <<EOF
apt-get update
apt-get install -y grub-efi-amd64 linux-image-amd64
mkdir /boot/efi
mount "${DEVICE}1" /boot/efi
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
update-grub
EOF
else
    echo "Unsupported bootloader type."
    exit 1
fi

# Clean up and unmount
echo "Cleaning up and unmounting..."
sudo umount -R "${TARGET}"

echo "Setup complete. You can now reboot into your new system."

# FILE: tools/disk/create_ubuntu_install.sh
#!/usr/bin/env bash

# Function to display error messages
error() {
    echo "Error: $1"
    exit 1
}

# Function to estimate partition sizes
estimate_partition_sizes() {
    ISO_SIZE=$(du -m "$ISO_PATH" | cut -f1)
    TOTAL_SIZE=$(sudo blockdev --getsize64 "$DRIVE")
    FIRST_PARTITION_SIZE_MB=10240  # Set the size for the first partition to 10GB

    if ((FIRST_PARTITION_SIZE_MB + ISO_SIZE > TOTAL_SIZE)); then
        error "Not enough space on the drive for the ISO file. Choose a larger drive or a smaller ISO."
    fi

    SECOND_PARTITION_SIZE_MB=$((TOTAL_SIZE - FIRST_PARTITION_SIZE_MB))

    echo "Estimated ISO size: ${ISO_SIZE}MB"
    echo "Estimated first partition size: ${FIRST_PARTITION_SIZE_MB}MB"
    echo "Estimated second partition size: ${SECOND_PARTITION_SIZE_MB}MB"

    echo -e "n\np\n1\n\n+${FIRST_PARTITION_SIZE_MB}M\nn\np\n2\n\n\nw\n" | fdisk "$DRIVE"
}

# Function to confirm destructive action
confirm_destructive_action() {
    echo "This script will destroy all data on the USB drive $DRIVE. Do you want to continue? (y/n): "
    read -r CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        echo "Aborting."
        exit 0
    fi
}

# Function to check if the ISO file already exists
check_existing_iso() {
    if [ -e "$ISO_PATH" ]; then
        echo "Warning: The ISO file already exists at $ISO_PATH."
        echo "Proceeding will overwrite the existing file."
        echo "Do you want to continue? (y/n): "
        read -r CONTINUE
        if [ "$CONTINUE" != "y" ]; then
            echo "Aborting."
            exit 0
        fi
    fi
}

# Function to unmount partitions
unmount_partitions() {
    echo "Unmounting partitions..."
    umount "$DRIVE"* 2>/dev/null || true
    sleep 1
}

# Function to format partitions
format_partitions() {
    echo "Formatting partitions..."
    mkfs.vfat "${DRIVE}1"
    mkfs.ext4 "${DRIVE}2"
}

# Function to write ISO to the first partition
write_iso_to_partition() {
    echo "Writing the ISO to the first partition..."
    dd if="$ISO_PATH" of="${DRIVE}1" bs=4M status=progress oflag=sync

    # Check for errors during dd
    if [ $? -eq 0 ]; then
        echo "ISO successfully written to the USB drive."
    else
        error "Error writing the ISO to the USB drive."
    fi
}

# Parse command line options
while getopts "rd:i:u:" opt; do
    case $opt in
        r)
            REFORMAT=true
            ;;
        d)
            DRIVE=$OPTARG
            ;;
        i)
            ISO_PATH=$OPTARG
            ;;
        u)
            ISO_URL=$OPTARG
            ;;
        \?)
            error "Invalid option: -$OPTARG"
            ;;
    esac
done

# Check if the drive variable is set
[ -z "$DRIVE" ] && error "Drive not specified. Use -d option to specify the drive."

# Check if the ISO_PATH variable is set
[ -z "$ISO_PATH" ] && error "ISO file not specified. Use -i option to specify the path to the ISO file."

# Check if the ISO_URL variable is set
[ -z "$ISO_URL" ] && error "ISO URL not specified. Use -u option to specify the URL to download the ISO file."

# Confirm destructive action
confirm_destructive_action

# Check if the ISO file already exists
check_existing_iso

# Unmount existing partitions
unmount_partitions

# If reformat option is specified, destroy existing data on the drive
if [ "$REFORMAT" = true ]; then
    echo "Destroying data on $DRIVE..."
    dd if=/dev/zero of="$DRIVE" bs=1M status=progress
    sleep 1
fi

sync

sudo partprobe "$DRIVE"

lsblk "$DRIVE"

# Estimate partition sizes
estimate_partition_sizes

# Unmount all partitions on the specified drive
for partition in "$DRIVE"*; do
    umount "$partition" 2>/dev/null || true
done

# Format partitions
format_partitions

# Download ISO using wget if it doesn't exist
if [ ! -e "$ISO_PATH" ]; then
    echo "Downloading Ubuntu ISO..."
    wget -O "$ISO_PATH" "$ISO_URL"
else
    echo "Using existing ISO file at $ISO_PATH."
fi

# Writing the ISO to the first partition
write_iso_to_partition

echo "Bootable USB creation completed. You can now boot from this USB drive to install Ubuntu."

lsblk "$DRIVE"

# FILE: tools/disk/format_drive.sh
#!/usr/bin/env bash

# Default values
ssd_device=""
check_local_drive=true

# Function to display usage information
usage() {
    echo "Usage: $0 -d <ssd_device> [-l] [-n]"
    echo "Options:"
    echo "  -d <ssd_device>  Specify the SSD device to partition and format."
    echo "  -l               Check if the specified device is a local drive (default)."
    echo "  -n               Skip the check if the specified device is a local drive."
    exit 1
}

# Function to confirm user action
confirm_action() {
    read -p "This will format $ssd_device. Are you sure? (y/n): " confirmation
    if [ "$confirmation" != "y" ]; then
        echo "Aborted."
        exit 0
    fi
}

# Parse command-line options
while getopts "d:ln" opt; do
  case $opt in
    d)
      ssd_device="/dev/$OPTARG"
      ;;
    l)
      check_local_drive=true
      ;;
    n)
      check_local_drive=false
      ;;
    \?)
      usage
      ;;
  esac
done

# Check if the SSD device is specified
if [ -z "$ssd_device" ]; then
    echo "Error: SSD device not specified."
    usage
fi

# Check if the specified device exists
if [ ! -b "$ssd_device" ]; then
    echo "Error: SSD device not found."
    usage
fi

# Check if the specified device is a local drive (optional)
if $check_local_drive; then
    local_drive=$(df -P "$ssd_device" | awk 'NR==2 {print $1}')
    if [ "$ssd_device" == "$local_drive" ]; then
        echo "Error: Attempting to format a local drive. Use the -n option to skip this check."
        usage
    fi
fi

# Confirm before proceeding
confirm_action

# Unmount all partitions on the SSD device
for partition in $(lsblk -n -o NAME -l "${ssd_device}"); do
    sudo umount "$partition" 2>/dev/null
done

# Disable swap partitions on the SSD device
for swap_partition in $(grep "${ssd_device}" /etc/fstab | grep swap | awk '{print $1}'); do
    sudo swapoff "$swap_partition"
done

# Wipe the device using wipefs
sudo wipefs --all "$ssd_device"

# Partition the SSD using fdisk
sudo fdisk "$ssd_device" <<EOF
o
n
p
1


w
EOF

# Unmount all partitions on the SSD device
for partition in $(lsblk -n -o NAME -l "${ssd_device}"); do
    sudo umount "$partition" 2>/dev/null
done

# Create a file system on the partition
sudo mkfs.ext4 "${ssd_device}1"  # You can add the size here if needed, e.g., 28G

# Eject the device using udisksctl
udisksctl unmount --block-device "$ssd_device" && udisksctl eject --block-device "$ssd_device"

echo "Single partition on $ssd_device created successfully, formatted, and ejected."

lsblk "${ssd_device}"

# FILE: tools/examples/gen_dnsmasq_config.py
#!/usr/bin/env python3
"""Generate an example dnsmasq configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSMasqConfigurator


def build_example_configuration() -> str:
    """Build an example dnsmasq configuration."""
    configurator = DNSMasqConfigurator()

    configurator.add_listen_port(53)
    configurator.enable_domain_filtering()
    configurator.enable_dnssec("/path/to/trust-anchors.conf")
    configurator.enable_dnssec_check_unsigned()
    configurator.enable_filter_windows_dns_requests()
    configurator.set_resolv_file("/etc/resolv.conf")
    configurator.set_strict_order()
    configurator.disable_resolv_conf()
    configurator.disable_poll_resolv_files()
    configurator.add_name_server("example.com", "203.0.113.1")
    configurator.add_reverse_server("192.168.0", "203.0.113.1")
    configurator.add_local_only_domain("mylocaldomain")
    configurator.force_domain_to_ip("example.net", "203.0.113.2")
    configurator.add_ipv6_address("ipv6.example.com", "2001:db8::1")
    configurator.add_query_ips_to_ipset(["example.org", "sub.example.org"], "myipset")
    configurator.add_query_ips_to_netfilter_sets(
        ["example.com", "sub.example.com"],
        ["set1", "set2"],
    )
    configurator.add_ipv6_addresses_to_netfilter_sets(["ipv6.example.com"], ["set3"])
    configurator.set_server_routing("203.0.113.3")
    configurator.set_uid_and_gid("dnsmasq", "dnsmasq")
    configurator.set_listen_interfaces(["eth0", "eth1"])
    configurator.set_except_interfaces(["eth2"])
    configurator.set_listen_addresses(["192.168.0.1", "192.168.1.1"])
    configurator.disable_dhcp_on_interface("eth0")
    configurator.bind_only_to_listened_interfaces()
    configurator.disable_etc_hosts()
    configurator.set_additional_hosts_file("/etc/extra-hosts")
    configurator.set_expand_hosts()
    configurator.set_domain("example.local")
    configurator.set_domain_for_subnet("example.net", "192.168.2.0")
    configurator.set_domain_for_range("example.org", "192.168.3.1", "192.168.3.10")
    configurator.add_dhcp4_range("192.168.0.100", "192.168.0.200", "12h")
    configurator.add_dhcp4_range_with_netmask(
        "192.168.1.50",
        "192.168.1.100",
        "255.255.255.0",
        "8h",
    )
    configurator.add_dhcp4_range_with_tag("mytag", "192.168.2.10", "192.168.2.20", "6h")
    configurator.set_tftp_server("/path/to/tftp")
    configurator.set_boot_file("pxelinux.0")
    configurator.add_pxe_boot_option(150, "pxelinux.0")
    configurator.add_dhcp_option(66, "203.0.113.4")
    configurator.add_dhcp_option(67, "bootfile")
    configurator.set_dhcp_authoritative()

    return configurator.generate_configuration()


def main() -> int:
    """Print the example config or write it to an explicit output path."""
    parser = argparse.ArgumentParser(description="Generate an example dnsmasq configuration.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output file. Defaults to stdout.",
    )
    args = parser.parse_args()

    config = build_example_configuration()
    if args.output:
        args.output.write_text(config, encoding="utf-8")
        return 0

    print(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# FILE: tools/git/README.md
# RouterShell Git Helpers

These scripts provide RouterShell Git workflow helpers adapted from the PyPNM
tooling style.

## Save Current Work

Run local quality gates, stage all changes, and create a timestamped commit:

```bash
./tools/git/git-save.sh --commit-msg "Add RouterShell packaging"
```

Push after committing:

```bash
./tools/git/git-save.sh --commit-msg "Add RouterShell packaging" --push
```

## Commit And Push

Create a commit and push the current branch:

```bash
./tools/git/git-push.sh --commit-msg "Add RouterShell packaging"
```

Pushing branches other than `main` or `hot-fix` requires confirmation.

## Reset Branch History

Rewrite a branch as a fresh orphan history:

```bash
./tools/git/git-reset-branch-history.sh --branch main --message "Initial RouterShell clean commit"
```

This command force-pushes. By default it creates a remote backup branch first.
Run it only when you intentionally want to rewrite branch history.

## Quality Gates

The save and push helpers run these RouterShell checks by default:

```bash
./tools/release/check_version.py
python3 -m py_compile routershell/__init__.py routershell/__main__.py routershell/_version.py routershell/cli.py lib/__init__.py
python3 -m compileall -q routershell lib tests tools/examples tools/hardware tools/release tools/support
find start.sh install tools -path "tools/agent-review" -prune -o -name "*.sh" -exec bash -n {} \;
```

If `pytest` or `ruff` are installed, the helpers also run:

```bash
python3 -m pytest
python3 -m ruff check .
```

Use `--skip-checks` only when you are intentionally saving work that is not
ready for validation.

# FILE: tools/git/git-common.sh
#!/usr/bin/env bash
set -euo pipefail

rs_run_check() {
  local label="$1"
  shift

  echo "[check] ${label}..."
  if "$@"; then
    echo "[pass]  ${label}"
  else
    echo "[fail]  ${label}" >&2
    exit 1
  fi
}

rs_require_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: This script must be run inside a Git repository." >&2
    exit 1
  fi
}

rs_repo_root() {
  git rev-parse --show-toplevel
}

rs_python() {
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi

  echo "ERROR: python3 or python is required." >&2
  exit 1
}

rs_run_quality_gates() {
  local python_bin
  python_bin="$(rs_python)"

  rs_run_check "pyproject metadata" "${python_bin}" - <<'PY'
import tomllib
from pathlib import Path

with Path("pyproject.toml").open("rb") as handle:
    pyproject = tomllib.load(handle)

assert pyproject["project"]["name"] == "routershell"
assert pyproject["project"]["scripts"]["routershell"] == "routershell.cli:main"
assert pyproject["project"]["scripts"]["routershell-factory-reset"] == "routershell.cli:factory_reset"
PY

  rs_run_check "version consistency" "${python_bin}" tools/release/check_version.py
  rs_run_check "compile packaging files" "${python_bin}" -m py_compile routershell/__init__.py routershell/__main__.py routershell/_version.py routershell/cli.py lib/__init__.py
  rs_run_check "compile source tree" "${python_bin}" -m compileall -q routershell lib tests tools/examples tools/hardware tools/release tools/support
  rs_run_check "shell syntax" bash -c 'find start.sh install tools -path "tools/agent-review" -prune -o -name "*.sh" -exec bash -n {} \;'

  if "${python_bin}" -m pytest --version >/dev/null 2>&1; then
    rs_run_check "pytest" "${python_bin}" -m pytest
  else
    echo "[skip]  pytest (not installed)"
  fi

  if "${python_bin}" -m ruff --version >/dev/null 2>&1; then
    rs_run_check "ruff check" "${python_bin}" -m ruff check .
  else
    echo "[skip]  ruff check (not installed)"
  fi
}

# FILE: tools/hardware/cpu_hw_summary.py
#!/usr/bin/env python3
"""Print a concise CPU hardware summary."""

from __future__ import annotations

import json
import subprocess

from tabulate import tabulate


def extract_field(data: list[dict[str, str]], field_name: str) -> str:
    """Return a named field from lscpu JSON output."""
    for item in data:
        if item["field"] == field_name:
            return item["data"]
    return "N/A"


def create_tabulated_summary() -> str:
    """Create a tabulated CPU summary from lscpu output."""
    try:
        result = subprocess.run(["lscpu", "-J"], capture_output=True, text=True, check=True)
        lscpu_json = result.stdout

        data = json.loads(lscpu_json)["lscpu"]

        architecture = extract_field(data, "Architecture:")
        cpu_count = extract_field(data, "CPU(s):")
        vendor_id = extract_field(data, "Vendor ID:")

        model_name = extract_field(data, "Model name:")
        cpu_family = extract_field(data, "CPU family:")
        model = extract_field(data, "Model:")
        thread_per_core = extract_field(data, "Thread(s) per core:")
        core_per_socket = extract_field(data, "Core(s) per socket:")
        socket_count = extract_field(data, "Socket(s):")
        cpu_max_mhz = extract_field(data, "CPU max MHz:")
        cpu_min_mhz = extract_field(data, "CPU min MHz:")
        bogo_mips = extract_field(data, "BogoMIPS:")

        virtualization = extract_field(data, "Virtualization:")

        table = [
            ["Model Name", model_name],
            ["Vendor ID", vendor_id],
            ["Model", model],
            ["Architecture", architecture],
            ["CPU(s)", cpu_count],
            ["CPU Family", cpu_family],
            ["Thread(s) per Core", thread_per_core],
            ["Core(s) per Socket", core_per_socket],
            ["Socket(s)", socket_count],
            ["CPU Min/Max MHz", f"{cpu_min_mhz}/{cpu_max_mhz}"],
            ["BogoMIPS", bogo_mips],
            ["Virtualization", virtualization],
        ]

        return tabulate(table, headers=["CPU", "Info"], tablefmt="simple")
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return f"Error: {exc}"


if __name__ == "__main__":
    print(create_tabulated_summary())

# FILE: tools/hardware/network_hw_detection.py
#!/usr/bin/env python3
"""Detect and summarize network hardware."""

from __future__ import annotations

import subprocess

from tabulate import tabulate


def detect_network_hardware() -> list[dict[str, str]]:
    """Return detected network interfaces from lshw output."""
    interface_info: list[dict[str, str]] = []

    try:
        network_info = subprocess.check_output(["sudo", "lshw", "-c", "network"], text=True)

        sections = network_info.split("*-network")

        for section in sections[1:]:
            lines = section.strip().split("\n")

            interface_data = {
                "Logical Name": "N/A",
                "Bus Info": "N/A",
                "Serial": "N/A",
                "Capacity": "N/A",
                "Type": "Unknown",
            }

            for line in lines:
                if "bus info:" in line:
                    interface_data["Bus Info"] = line.split("bus info:")[1].strip()
                elif "logical name:" in line:
                    interface_data["Logical Name"] = line.split("logical name:")[1].strip()
                elif "serial:" in line:
                    interface_data["Serial"] = line.split("serial:")[1].strip()
                elif "configuration:" in line:
                    configuration = line.split("configuration:")[1].strip()
                    if "pci@" in interface_data["Bus Info"] and "wireless" in configuration.lower():
                        interface_data["Type"] = "Wireless"
                elif "capacity:" in line:
                    interface_data["Capacity"] = line.split("capacity:")[1].strip()

            if "usb@" in interface_data["Bus Info"]:
                interface_data["Type"] = "USB-Ethernet"
            elif "pci@" in interface_data["Bus Info"] and "Wireless" not in interface_data["Type"]:
                interface_data["Type"] = "PCI-Ethernet"

            interface_info.append(interface_data)

    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}")

    return interface_info


if __name__ == "__main__":
    detected_interfaces = detect_network_hardware()

    headers = ["Logical Name", "Bus Info", "Serial", "Capacity", "Type"]
    table_data = [
        [
            interface["Logical Name"],
            interface["Bus Info"],
            interface["Serial"],
            interface["Capacity"],
            interface["Type"],
        ]
        for interface in detected_interfaces
    ]

    print(tabulate(table_data, headers, tablefmt="simple"))

# FILE: tools/hardware/usb_to_ethernet_find.sh
#!/usr/bin/env bash

# Function to check if a device is a USB to Ethernet adapter based on bus info
is_usb_to_eth() {
  local bus_info="$1"
  
  # Check if the bus info indicates a USB device
  if [[ "$bus_info" == *"usb"* ]]; then
    return 0  # Return success if it's a USB to Ethernet adapter
  fi
  return 1  # Return failure by default
}

# Get the network interfaces using lshw
network_info=$(lshw -c network)

# Initialize variables to store bus info and interface name
current_bus_info=""
current_interface=""

# Iterate through network interfaces and check if they are USB to Ethernet adapters
while read -r line; do
  if [[ "$line" == *"bus info:"* ]]; then
    # Extract bus info from the line
    bus_info=$(echo "$line" | awk -F ' ' '{print $3}')
    if is_usb_to_eth "$bus_info"; then
      # If it's a USB to Ethernet adapter, store the bus info
      current_bus_info="$bus_info"
    else
      # If it's not a USB to Ethernet adapter, reset the stored bus info
      current_bus_info=""
    fi
  elif [[ "$line" == *"logical name:"* ]]; then
    # Extract the logical name from the line
    current_interface=$(echo "$line" | awk -F ' ' '{print $3}')
    if [[ -n "$current_bus_info" ]]; then
      # If a USB to Ethernet adapter was found, print its interface name
      echo "USB to Ethernet adapter found: $current_interface"
      # Reset the stored bus info for the next iteration
      current_bus_info=""
    fi
  fi
done <<< "$network_info"

# FILE: tools/network/bridge_control_options.sh
#!/usr/bin/env bash

vif_names=("loopback10" "loopback11" "loopback12" "loopback13")

# Function to create virtual interfaces
create_virtual_interfaces() {
  local peers="$1"  # "yes" or "no" to create with or without peers

  for vif in "${vif_names[@]}"; do
    if [ "$peers" == "yes" ]; then
      ip link add "$vif" type veth peer name "$vif"_peer
    else
      ip link add "$vif" type veth
    fi
    ip link set "$vif" up
  done

  local message="Virtual interfaces created"
  [ "$peers" == "yes" ] && message+=" with peers"
  echo "$message: ${vif_names[*]}"
}

# Function to create the bridge and add virtual interfaces
create_bridge() {
  bridge_name="br10"

  # Create the bridge
  ip link add name "$bridge_name" type bridge
  ip link set "$bridge_name" up

  # Add virtual interfaces to the bridge
  for vif in "${vif_names[@]}"; do
    ip link set "$vif" master "$bridge_name"
    ip link set "$vif" up
  done

  echo "Bridge '$bridge_name' created and virtual interfaces added."
}

# Function to delete the bridge and virtual interfaces
delete_bridge() {
  bridge_name="br10"

  # Remove virtual interfaces from the bridge and delete them
  for vif in "${vif_names[@]}"; do
    ip link set "$vif" nomaster
    ip link delete "$vif"
  done

  # Delete the bridge
  ip link set "$bridge_name" down
  ip link delete "$bridge_name"

  echo "Bridge '$bridge_name' and virtual interfaces deleted."
}

# Function to show information about the bridge
show_bridge() {
  bridge_name="br10"

  # Display bridge information
  echo "Bridge Information"
  ip addr show
  echo
  echo
  echo "Bridge Information"
  brctl show
}

# Function to show information about virtual interfaces
show_interfaces() {

  for vif in "${vif_names[@]}"; do
    echo "Interface Information for $vif:"
    ip addr show "$vif"
    echo
  done
}

# Main script
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [-c create_peers | -C create_no_peers | -d destroy | -s show | -i show_interfaces]"
  exit 1
fi

option="$1"

case "$option" in
  "-c" | "create_peers")
    create_virtual_interfaces "yes"
    create_bridge
    ;;
  "-C" | "create_no_peers")
    create_virtual_interfaces "no"
    create_bridge
    ;;
  "-d" | "destroy")
    delete_bridge
    ;;
  "-s" | "show")
    show_bridge
    ;;
  "-i" | "show_interfaces")
    show_interfaces
    ;;
  *)
    echo "Invalid option: $option. Use '-c' or 'create_peers' to create with peers, '-C' or 'create_no_peers' to create without peers, '-d' or 'destroy' to delete, '-s' or 'show' to display bridge info, '-i' or 'show_interfaces' to display interface info."
    exit 1
    ;;
esac

exit 0

# FILE: tools/network/configure_nat.sh
#!/usr/bin/env bash

# Function to list available network interfaces
list_interfaces() {
    echo "Available network interfaces:"
    echo "-----------------------------"
    interfaces=($(ip link show | awk -F ': ' '{print $2}' | grep -v lo))
    for ((i = 0; i < ${#interfaces[@]}; i++)); do
        echo "$i: ${interfaces[i]}"
    done
}

# Function to create NAT
create_nat() {
    list_interfaces
    echo
    read -p "Enter the number of the internal interface (e.g., 0, 1, etc.): " internal_index

    if [[ ! $internal_index =~ ^[0-9]+$ || $internal_index -ge ${#interfaces[@]} ]]; then
        echo "Invalid input. Please select a valid interface number."
        return
    fi

    internal_interface="${interfaces[internal_index]}"

    # Find the first non-loopback interface as the external interface
    external_interface=$(ip link show | awk -F ': ' '{print $2}' | grep -v lo | grep -v "$internal_interface" | head -n 1)

    if [[ -z "$external_interface" ]]; then
        echo "Error: No suitable external interface found."
        return
    fi

    echo "Configuring NAT on $internal_interface (internal) and $external_interface (external)..."
    
    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward
    
    # Enable masquerading (SNAT) for outbound traffic
    iptables -t nat -A POSTROUTING -o $external_interface -j MASQUERADE
    
    # Check if the directory for iptables rules exists, and create it if necessary
    if [[ ! -d /etc/iptables ]]; then
        mkdir /etc/iptables
    fi
    
    # Save the iptables rules to make them persistent across reboots
    iptables-save > /etc/iptables/rules.v4
    
    echo "NAT configuration is complete."
}

# Function to destroy NAT
destroy_nat() {
    echo "Destroying NAT configuration..."
    
    # Disable IP forwarding
    echo 0 > /proc/sys/net/ipv4/ip_forward
    
    # Flush and delete NAT rules
    iptables -t nat -F
    iptables -t nat -X

    # Check if the directory for iptables rules exists
    if [[ -d /etc/iptables ]]; then
        # Delete the saved iptables rules file
        rm /etc/iptables/rules.v4
    fi
    
    echo "NAT configuration has been destroyed."
}

# Main menu
while true; do
    echo
    echo "Network Address Translation (NAT) Configuration"
    echo "--------------------------------------------"
    echo "1. Create NAT"
    echo "2. Destroy NAT"
    echo "3. Exit"
    read -p "Select an option (1/2/3): " choice

    case $choice in
        1)
            create_nat
            ;;
        2)
            destroy_nat
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select a valid option."
            ;;
    esac
done

# FILE: tools/network/create_complete_network.sh
#!/usr/bin/env bash

# Function to create bridges and virtual interfaces
create_network() {
  local vlan="$1"
  local nvif="$2"
  local ip_cidr="$3"
  local gateway="$4"
  local bridge_name="br$vlan"
  
  # Extract IP address and subnet mask from CIDR notation
  ip_addr=$(echo "$ip_cidr" | cut -d'/' -f1)
  subnet_mask=$(echo "$ip_cidr" | cut -d'/' -f2)
  
  # Create the bridge and assign the VLAN
  brctl addbr "$bridge_name"
  ip link set "$bridge_name" up
  ip link add link "$bridge_name" name "$bridge_name.$vlan" type vlan id "$vlan"
  ip link set "$bridge_name.$vlan" up
  
  # Create and configure virtual interfaces for the bridge
  for i in $(seq 0 $((nvif - 1))); do
    ip link add link "$bridge_name" name "$bridge_name-vif$i" type veth peer name "$bridge_name-vif$i-peer"
    ip link set "$bridge_name-vif$i" up
    ip link set "$bridge_name-vif$i-peer" up
    ip link set "$bridge_name-vif$i" master "$bridge_name"
    ip link set "$bridge_name-vif$i-peer" master "$bridge_name"
  done
  
  # Set the IP address and default gateway for the bridge
  ip addr add "$ip_addr/$subnet_mask" dev "$bridge_name.$vlan"
  ip route add default via "$gateway" dev "$bridge_name.$vlan"
}

# Function to destroy bridges and virtual interfaces
destroy_network() {
  local vlan="$1"
  local bridge_name="br$vlan"

  # Turn down the bridge interface
  ip link set "$bridge_name" down

  # Remove virtual interfaces
  for iface in $(ip link show | grep "$bridge_name-vif" | awk -F: '{print $2}' | awk '{print $1}'); do
    ip link delete "$iface"
  done

  # Remove VLAN interface
  ip link delete "$bridge_name.$vlan"

  # Remove the bridge itself
  brctl delbr "$bridge_name"

  echo "Network with VLAN $vlan and bridge $bridge_name destroyed."
}

# Function to display the current network configuration
view_network() {
  local vlan="$1"
  local bridge_name="br$vlan"

  echo "Network Configuration for VLAN $vlan:"
  echo "Bridge Name: $bridge_name"
  
  # Display virtual interfaces
  echo "Virtual Interfaces:"
  for iface in $(ip link show | grep "$bridge_name-vif" | awk -F: '{print $2}' | awk '{print $1}'); do
    echo "  $iface"
  done
  
  # Display VLAN interface
  echo "VLAN Interface: $bridge_name.$vlan"

  # Display IP address and default gateway
  local ip_info=$(ip addr show dev "$bridge_name.$vlan" | grep "inet ")
  local gateway_info=$(ip route show dev "$bridge_name.$vlan" | grep "default via")
  
  echo "IP Address and Subnet Mask: $ip_info"
  echo "Default Gateway: $gateway_info"
}

# Display usage information
usage() {
  echo "Usage: $0 -c|-d|-v -vlan VLAN_ID -nvif NUM_VIF -ip IP_ADDRESS -gw GATEWAY [-debug]"
  echo "  -c          Create network"
  echo "  -d          Destroy network"
  echo "  -v          View network configuration"
  echo "  -vlan       VLAN ID (e.g., 1000)"
  echo "  -nvif       Number of virtual interfaces (e.g., 4)"
  echo "  -ip         IP address in CIDR notation (e.g., 192.168.1.1/24)"
  echo "  -gw         Gateway IP address (e.g., 192.168.1.254)"
  echo "  -debug      Debug mode (optional)"
  exit 1
}

# Debug function to display options
debug_options() {
  echo "Action: $action"
  echo "VLAN ID: $vlan"
  echo "Number of VIFs: $nvif"
  echo "IP Address: $ip_cidr"
  echo "Gateway: $gateway"
  echo "Debug Mode: $debug"
}

# Initialize debug mode as false
debug="false"

# Check for command-line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c)
      action="-c"
      ;;
    -d)
      action="-d"
      ;;
    -v)
      action="-v"
      ;;
    -vlan)
      vlan="$2"
      shift
      ;;
    -nvif)
      nvif="$2"
      shift
      ;;
    -ip)
      ip_cidr="$2"
      shift
      ;;
    -gw)
      gateway="$2"
      shift
      ;;
    -debug)
      debug="true"
      ;;
    *)
      usage
      ;;
  esac
  shift
done

# If debug mode is enabled, display options and exit
if [ "$debug" == "true" ]; then
  debug_options
  exit 0
fi

# Check if the action is "-c" (create), "-d" (destroy), or "-v" (view)
case "$action" in
  -c)
    create_network "$vlan" "$nvif" "$ip_cidr" "$gateway"
    ;;
  -d)
    destroy_network "$vlan"
    ;;
  -v)
    view_network "$vlan"
    ;;
  *)
    usage
    ;;
esac

# FILE: tools/network/reset_network.sh
#!/usr/bin/env bash

# Remove all VLANs
for vlan in $(ls /proc/net/vlan/ | grep ^vlan); do
    sudo vconfig rem $vlan
done

# Remove all bridges
for bridge in $(brctl show | awk 'NR>1 {print $1}'); do
    sudo brctl delbr $bridge
done

# Reset IPtables Rules
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo iptables -t mangle -F
sudo iptables -t mangle -X
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT

# Reset IPv6tables Rules (if using IPv6)
sudo ip6tables -F
sudo ip6tables -X
sudo ip6tables -t nat -F
sudo ip6tables -t nat -X
sudo ip6tables -t mangle -F
sudo ip6tables -t mangle -X
sudo ip6tables -P INPUT ACCEPT
sudo ip6tables -P FORWARD ACCEPT
sudo ip6tables -P OUTPUT ACCEPT

# Flush Route Table
sudo ip route flush table all

# Restart Network Interfaces
sudo ifdown -a
sudo ifup -a

# Restart Networking Service
if command -v service &> /dev/null; then
    sudo service networking restart
elif command -v systemctl &> /dev/null; then
    sudo systemctl restart networking
else
    echo "Unable to determine the service management tool. Please restart networking manually."
fi

echo "Networking stack and VLANs/bridges reset completed."

# FILE: tools/network/toggle_interface_state.sh
#!/usr/bin/env bash

# Function to display a numbered list of network interfaces with their current state
display_interfaces() {
  echo "Available Network Interfaces:"
  echo -e "Index\tInterface\tState"
  interfaces=($(ifconfig -s -a | awk '{print $1}' | sed -n '2,$p'))
  for ((i=0; i<${#interfaces[@]}; i++)); do
    interface="${interfaces[$i]}"
    state=$(ifconfig "$interface" | grep -q "UP" && echo "UP" || echo "DOWN")
    echo -e "$i\t$interface\t$state"
  done
}

# Function to toggle the selected network interface
toggle_interface() {
  read -p "Enter the number of the interface to toggle: " choice

  # Check if the input is a valid number
  if [[ ! $choice =~ ^[0-9]+$ ]]; then
    echo "Invalid input. Please enter a valid number."
    return
  fi

  # Check if the selected number is within the range of available interfaces
  if ((choice < 0 || choice >= ${#interfaces[@]})); then
    echo "Invalid interface number. Please select a number from the list."
    return
  fi

  selected_interface="${interfaces[$choice]}"

  # Check if the selected interface is currently up or down and toggle it
  if ifconfig "$selected_interface" | grep -q "UP"; then
    echo "Disabling interface $selected_interface..."
    sudo ifconfig "$selected_interface" down
    echo "Interface $selected_interface is now disabled."
  else
    echo "Enabling interface $selected_interface..."
    sudo ifconfig "$selected_interface" up
    echo "Interface $selected_interface is now enabled."
  fi
}

# Main script
clear
display_interfaces
toggle_interface

# FILE: tools/network/vlan_create.sh
#!/usr/bin/env bash

# Check if the script is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Function to list available network interfaces
list_interfaces() {
    echo "Available network interfaces:"
    ip -o link show | awk -F': ' '{print $2}'
}

# Function to create a VLAN interface
create_vlan() {
    interface="$1"
    vlan_id="$2"

    # Check if the VLAN ID already exists
    existing_vlans=$(ip -d link show type vlan | grep "vlan$id")
    if [[ $existing_vlans =~ vlan$id ]]; then
        echo "VLAN ID $vlan_id already exists."
        exit 1
    fi

    # Create the VLAN interface
    ip link add link "$interface" name "vlan$vlan_id" type vlan id "$vlan_id"

    # Bring up the VLAN interface
    ip link set "vlan$vlan_id" up

    echo "Created VLAN interface vlan$vlan_id"
}

# Main script
list_interfaces

while true; do
    read -p "Enter the name of the physical interface: " interface

    if [ -z "$interface" ]; then
        echo "Please enter a valid interface name."
    elif ! ip link show dev "$interface" &>/dev/null; then
        echo "Interface $interface does not exist."
    else
        break
    fi
done

while true; do
    read -p "Enter the VLAN ID you want to create: " vlan_id

    if [ -z "$vlan_id" ]; then
        echo "Please enter a valid VLAN ID."
    else
        create_vlan "$interface" "$vlan_id"
        break
    fi
done

# FILE: tools/network/vlan_destroy.sh
#!/usr/bin/env bash

# Check if the script is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Function to display existing VLAN interfaces
list_existing_vlans() {
    echo "Existing VLAN interfaces:"
    ip -o link show type vlan | awk -F': ' '{split($2, a, "@"); print a[1] " -> " a[2]}'
}

# Main script
list_existing_vlans

# Ask the user to select a VLAN to delete
read -p "Enter the VLAN ID you want to remove: " vlan_id

# Check if the VLAN interface exists
if ip -o link show | grep -q "vlan$vlan_id@"; then
    ip link delete "vlan$vlan_id"
    if [[ $? -eq 0 ]]; then
        echo "Removed VLAN interface vlan$vlan_id"
    else
        echo "Failed to remove VLAN interface vlan$vlan_id"
    fi
else
    echo "VLAN interface vlan$vlan_id does not exist."
fi

# FILE: tools/network/vlan_show.sh
#!/usr/bin/env bash

# Check if the script is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)."
    exit 1
fi

# Function to display VLAN information
show_vlans() {
    echo "VLAN information:"
    ip -o link show type vlan | awk -F'[@ ]' '{print $2, $3}' | sed 's/:$//'
}

# Main script
show_vlans

# FILE: tools/network/wlan_access_point.sh
#!/usr/bin/env bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root."
  exit 1
fi

# Set your network details
SSID="YourNetworkName"
PASSPHRASE="YourPassphrase"
INTERFACE="wlan0"
IP_ADDRESS="192.168.1.1/24"

# Stop network managers that may interfere
systemctl stop NetworkManager
systemctl stop wpa_supplicant

# Configure the wireless interface using ip
ip link set $INTERFACE up
ip address add $IP_ADDRESS dev $INTERFACE

# Create a Kea DHCP configuration file
cat <<EOL > /etc/kea/kea-dhcp4.conf
{
  "Dhcp4": {
    "interfaces-config": {
      "interfaces": [ "$INTERFACE" ]
    },
    "subnet4": [
      {
        "subnet": "192.168.1.0/24",
        "pools": [ { "pool": "192.168.1.2 - 192.168.1.254" } ],
        "option-data": [
          {
            "name": "routers",
            "data": "192.168.1.1"
          },
          {
            "name": "domain-name-servers",
            "data": "8.8.8.8, 8.8.4.4"
          }
        ]
      }
    ]
  }
}
EOL

# Start the Kea DHCP server
systemctl start kea-dhcp4

# Create a hostapd configuration file
cat <<EOL > /etc/hostapd/hostapd.conf
interface=$INTERFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSPHRASE
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOL

# Start the access point using hostapd
systemctl start hostapd

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Configure IP tables to allow NAT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Save the IP tables rules
iptables-save > /etc/iptables.ipv4.nat

# Set up IP tables restore on boot
echo "up iptables-restore < /etc/iptables.ipv4.nat" >> /etc/network/interfaces

# Restart networking to apply changes
systemctl restart networking

echo "Wireless Access Point configured successfully!"

# FILE: tools/reference/tools-layout.md
<!-- SPDX-License-Identifier: GPL-2.0-or-later -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell Tools Layout

Tools are grouped by purpose so destructive host operations are easier to
identify before running them.

## Categories

- `agent-review/`: Coding-agent review bundles for completed tasks.
- `dev/`: Local development cleanup helpers.
- `disk/`: Disk inspection, formatting, and boot media helpers. These can be
  destructive.
- `examples/`: Example generators and usage demonstrations. Examples should not
  modify system files unless an explicit output path or flag is provided.
- `git/`: RouterShell Git save, push, and branch-history helpers.
- `hardware/`: Host hardware inspection helpers.
- `network/`: Network lab and interface mutation helpers. These can change host
  links, routes, firewall state, and wireless services.
- `reference/`: Captured command references and static notes.
- `release/`: Version checks, release automation, and release reports.
- `services/`: Service setup, teardown, and simulation helpers. These can
  install, remove, start, or stop host services.
- `support/`: Small support helpers used by release or workflow scripts.
- `vm/`: Disposable VM workflows for installer testing.

## Safety

Review scripts under `disk/`, `network/`, and `services/` before running them.
Prefer disposable VM testing for workflows that can alter host networking,
packages, disks, or service state.

# FILE: tools/reference/wi.txt
Usage:	iw [options] command
Options:
	--debug		enable netlink debugging
	--version	show version (5.16)
Commands:
	dev <devname> ap start 
	dev <devname> ap stop 
	phy <phyname> coalesce enable <config-file>
	phy <phyname> coalesce disable 
	phy <phyname> coalesce show 
	dev <devname> disconnect
	dev <devname> connect [-w] <SSID> [<freq in MHz>] [<bssid>] [auth open|shared] [key 0:abcde d:1:6162636465] [mfp:req/opt/no]
	dev <devname> auth <SSID> <bssid> <type:open|shared> <freq in MHz> [key 0:abcde d:1:6162636465]
	dev <devname> cqm rssi <threshold|off> [<hysteresis>]
	event [-t|-T|-r] [-f]
	dev <devname> ftm get_stats 
	dev <devname> ftm start_responder [lci=<lci buffer in hex>] [civic=<civic buffer in hex>]
	phy <phyname> hwsim getps 
	phy <phyname> hwsim setps <value>
	phy <phyname> hwsim stopqueues 
	phy <phyname> hwsim wakequeues 
	dev <devname> ibss leave
	dev <devname> ibss join <SSID> <freq in MHz> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz] [fixed-freq] [<fixed bssid>] [beacon-interval <TU>] [basic-rates <rate in Mbps,rate2,...>] [mcast-rate <rate in Mbps>] [key d:0:abcde]
	phy <phyname> info
	list
	phy
	commands
	features 
	phy <phyname> interface add <name> type <type> [mesh_id <meshid>] [4addr on|off] [flags <flag>*] [addr <mac-addr>]
	dev <devname> interface add <name> type <type> [mesh_id <meshid>] [4addr on|off] [flags <flag>*] [addr <mac-addr>]
	dev <devname> del
	dev <devname> info
	dev
	dev <devname> switch freq <freq> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz] [beacons <count>] [block-tx]
	dev <devname> switch freq <control freq> [5|10|20|40|80|80+80|160] [<center1_freq> [<center2_freq>]] [beacons <count>] [block-tx]
	dev <devname> switch channel <channel> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz] [beacons <count>] [block-tx]
	help [command]
	dev <devname> link
	dev <devname> measurement ftm_request <config-file> [timeout=<seconds>] [randomise[=<addr>/<mask>]]
	dev <devname> mesh join <mesh ID> [[freq <freq in MHz> <NOHT|HT20|HT40+|HT40-|80MHz>] [basic-rates <rate in Mbps,rate2,...>]], [mcast-rate <rate in Mbps>] [beacon-interval <time in TUs>] [dtim-period <value>] [vendor_sync on|off] [<param>=<value>]*
	dev <devname> mesh leave
	dev <devname> mesh_param dump 
	dev <devname> mgmt dump frame <type as hex ab> <pattern as hex ab:cd:..> [frame <type> <pattern>]* [count <frames>]
	dev <devname> mpath probe <destination MAC address> frame <frame>
	dev <devname> mpath get <MAC address>
	dev <devname> mpath del <MAC address>
	dev <devname> mpath new <destination MAC address> next_hop <next hop MAC address>
	dev <devname> mpath set <destination MAC address> next_hop <next hop MAC address>
	dev <devname> mpath dump
	dev <devname> mpp get <MAC address>
	dev <devname> mpp dump
	wdev <idx> nan start pref <pref> [bands [2GHz] [5GHz]]
	wdev <idx> nan stop 
	wdev <idx> nan config [pref <pref>] [bands [2GHz] [5GHz]]
	wdev <idx> nan rm_func cookie <cookie>
	wdev <idx> nan add_func type <publish|subscribe|followup> [active] [solicited] [unsolicited] [bcast] [close_range] name <name> [info <info>] [flw_up_id <id> flw_up_req_id <id> flw_up_dest <mac>] [ttl <ttl>] [srf <include|exclude> <bf|list> [bf_idx] [bf_len] <mac1;mac2...>] [rx_filter <str1:str2...>] [tx_filter <str1:str2...>]
	dev <devname> ocb join <freq in MHz> <5MHz|10MHz>
	dev <devname> ocb leave
	dev <devname> offchannel <freq> <duration>
	wdev <idx> p2p start 
	wdev <idx> p2p stop 
	phy <phyname> channels
	dev <devname> cac channel <channel> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz]
	dev <devname> cac freq <freq> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz]
	dev <devname> cac freq <control freq> [5|10|20|40|80|80+80|160] [<center1_freq> [<center2_freq>]]
	dev <devname> cac trigger channel <channel> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz]
	dev <devname> cac trigger freq <frequency> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz]
	dev <devname> cac trigger freq <frequency> [5|10|20|40|80|80+80|160] [<center1_freq> [<center2_freq>]]
	reg set <ISO/IEC 3166-1 alpha2>
	reg get
	phy <phyname> reg get
	reg reload
	dev <devname> roc start <freq> <time in ms>
	dev <devname> scan [-u] [freq <freq>*] [duration <dur>] [ies <hex as 00:11:..>] [meshid <meshid>] [lowpri,flush,ap-force,duration-mandatory] [randomise[=<addr>/<mask>]] [ssid <ssid>*|passive]
	dev <devname> scan dump [-u]
	dev <devname> scan trigger [freq <freq>*] [duration <dur>] [ies <hex as 00:11:..>] [meshid <meshid>] [lowpri,flush,ap-force,duration-mandatory,coloc] [randomise[=<addr>/<mask>]] [ssid <ssid>*|passive]
	dev <devname> scan abort 
	dev <devname> scan sched_start [interval <in_msecs> | scan_plans [<interval_secs:iterations>*] <interval_secs>] [delay <in_secs>] [freqs <freq>+] [matches [ssid <ssid>]+]] [active [ssid <ssid>]+|passive] [randomise[=<addr>/<mask>]] [coloc] [flush]
	dev <devname> scan sched_stop 
	dev <devname> get mesh_param [<param>]
	phy <phyname> get txq 
	dev <devname> get power_save 
	dev <devname> set bitrates [legacy-<2.4|5> <legacy rate in Mbps>*] [ht-mcs-<2.4|5> <MCS index>*] [vht-mcs-<2.4|5> [he-mcs-<2.4|5|6> <NSS:MCSx,MCSy... | NSS:MCSx-MCSy>*] [sgi-2.4|lgi-2.4] [sgi-5|lgi-5] [he-gi-<2.4|5|6> <0.8|1.6|3.2>] [he-ltf-<2.4|5|6> <1|2|4>]
	dev <devname> set monitor <flag>*
	dev <devname> set meshid <meshid>
	dev <devname> set type <type>
	dev <devname> set 4addr <on|off>
	dev <devname> set noack_map <map>
	dev <devname> set peer <MAC address>
	dev <devname> set mcast_rate <rate in Mbps>
	dev <devname> set tidconf [peer <MAC address>] tids <mask> [override] [sretry <num>] [lretry <num>] [ampdu [on|off]] [amsdu [on|off]] [noack [on|off]] [rtscts [on|off]][bitrates <type [auto|fixed|limit]> [legacy-<2.4|5> <legacy rate in Mbps>*] [ht-mcs-<2.4|5> <MCS index>*] [vht-mcs-<2.4|5> <NSS:MCSx,MCSy... | NSS:MCSx-MCSy>*] [sgi-2.4|lgi-2.4] [sgi-5|lgi-5]]
	dev <devname> set mesh_param <param>=<value> [<param>=<value>]*
	phy <phyname> set name <new name>
	phy <phyname> set freq <freq> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz|160MHz]
	phy <phyname> set freq <control freq> [5|10|20|40|80|80+80|160] [<center1_freq> [<center2_freq>]]
	dev <devname> set freq <freq> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz|160MHz]
	dev <devname> set freq <control freq> [5|10|20|40|80|80+80|160] [<center1_freq> [<center2_freq>]]
	phy <phyname> set channel <channel> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz|160MHz]
	dev <devname> set channel <channel> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz|160MHz]
	phy <phyname> set frag <fragmentation threshold|off>
	phy <phyname> set rts <rts threshold|off>
	phy <phyname> set retry [short <limit>] [long <limit>]
	phy <phyname> set netns { <pid> | name <nsname> }
	phy <phyname> set coverage <coverage class>
	phy <phyname> set distance <auto|distance>
	phy <phyname> set txpower <auto|fixed|limit> [<tx power in mBm>]
	dev <devname> set txpower <auto|fixed|limit> [<tx power in mBm>]
	phy <phyname> set antenna <bitmap> | all | <tx bitmap> <rx bitmap>
	phy <phyname> set txq limit <packets> | memory_limit <bytes> | quantum <bytes>
	dev <devname> set power_save <on|off>
	phy <phyname> set sar_specs <sar type> <range index:sar power>*
	dev <devname> survey dump
	dev <devname> vendor send <oui> <subcmd> <filename|-|hex data>
	dev <devname> vendor recv <oui> <subcmd> <filename|-|hex data>
	dev <devname> vendor recvbin <oui> <subcmd> <filename|-|hex data>
	phy <phyname> wowlan enable [any] [disconnect] [magic-packet] [gtk-rekey-failure] [eap-identity-request] [4way-handshake] [rfkill-release] [net-detect [interval <in_msecs> | scan_plans [<interval_secs:iterations>*] <interval_secs>] [delay <in_secs>] [freqs <freq>+] [matches [ssid <ssid>]+]] [active [ssid <ssid>]+|passive] [randomise[=<addr>/<mask>]] [coloc] [flush]] [tcp <config-file>] [patterns [offset1+]<pattern1> ...]
	phy <phyname> wowlan disable 
	phy <phyname> wowlan show 
	dev <devname> station get <MAC address>
	dev <devname> station del <MAC address> [subtype <subtype>] [reason-code <code>]
	dev <devname> station dump [-v]
	dev <devname> station set <MAC address> txpwr <auto|limit> [<tx power dBm>]
	dev <devname> station set <MAC address> airtime_weight <weight>
	dev <devname> station set <MAC address> mesh_power_mode <active|light|deep>
	dev <devname> station set <MAC address> vlan <ifindex>
	dev <devname> station set <MAC address> plink_action <open|block>

Commands that use the netdev ('dev') can also be given the
'wdev' instead to identify the device.

You can omit the 'phy' or 'dev' if the identification is unique,
e.g. "iw wlan0 info" or "iw phy0 info". (Don't when scripting.)

Do NOT screenscrape this tool, we don't consider its output stable.


# FILE: tools/release/test-runner.py
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""RouterShell unittest discovery runner."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TestResult:
    """Container for individual test file results."""

    file_path: str
    tests_run: int
    failures: int
    errors: int
    skipped: int
    success: bool
    duration: float


@dataclass
class TestSummary:
    """Container for overall test execution summary."""

    total_files: int
    successful_files: int
    failed_files: int
    total_tests: int
    total_failures: int
    total_errors: int
    total_skipped: int
    total_duration: float
    results: list[TestResult]


class RouterShellTestRunner:
    """Discover and run unittest-compatible tests."""

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser."""
        parser = argparse.ArgumentParser(description="Run RouterShell unittest tests.")
        parser.add_argument("--tests-dir", default="tests", help="Directory containing tests.")
        parser.add_argument("--pattern", default="test_*.py", help="Test file pattern.")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
        parser.add_argument("--failfast", action="store_true", help="Stop on first failure.")
        parser.add_argument("--json-report", action="store_true", help="Write a JSON report.")
        parser.add_argument("--output-dir", default="test_reports", help="Report output directory.")
        return parser

    @staticmethod
    def _discover(tests_dir: Path, pattern: str) -> list[Path]:
        """Discover test files."""
        if not tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {tests_dir}")
        return sorted(tests_dir.rglob(pattern))

    @staticmethod
    def _run_file(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run tests from one file."""
        start = time.time()
        loader = unittest.TestLoader()
        suite = loader.discover(str(path.parent), pattern=path.name)
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1, failfast=failfast)
        result = runner.run(suite)
        tests_run = result.testsRun
        errors = len(result.errors)
        failures = len(result.failures)

        if tests_run == 0:
            function_result = RouterShellTestRunner._run_function_tests(path, verbose, failfast)
            tests_run = function_result.tests_run
            errors = errors + function_result.errors
            failures = failures + function_result.failures

        return TestResult(
            file_path=str(path),
            tests_run=tests_run,
            failures=failures,
            errors=errors,
            skipped=len(result.skipped),
            success=failures == 0 and errors == 0,
            duration=time.time() - start,
        )

    @staticmethod
    def _run_function_tests(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run pytest-style module-level test functions without pytest."""
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            return TestResult(str(path), 0, 0, 1, 0, False, 0.0)

        module = importlib.util.module_from_spec(spec)
        project_root = Path.cwd()
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path = original_path

        functions = [
            value
            for name, value in vars(module).items()
            if name.startswith("test_") and callable(value)
        ]
        failures = 0
        errors = 0
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        for function in functions:
            try:
                function()
                if verbose:
                    print(f"PASS {function.__name__}")
            except AssertionError:
                failures = failures + 1
                traceback.print_exc()
                if failfast:
                    break
            except Exception:
                errors = errors + 1
                traceback.print_exc()
                if failfast:
                    break
        sys.path = original_path

        return TestResult(
            file_path=str(path),
            tests_run=len(functions),
            failures=failures,
            errors=errors,
            skipped=0,
            success=failures == 0 and errors == 0,
            duration=0.0,
        )

    @staticmethod
    def _write_json(summary: TestSummary, output_dir: Path) -> None:
        """Write a JSON test report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "summary": {
                "total_files": summary.total_files,
                "successful_files": summary.successful_files,
                "failed_files": summary.failed_files,
                "total_tests": summary.total_tests,
                "total_failures": summary.total_failures,
                "total_errors": summary.total_errors,
                "total_skipped": summary.total_skipped,
                "total_duration": summary.total_duration,
            },
            "results": [result.__dict__ for result in summary.results],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON report generated: {output_path}")

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Run discovered tests and return a process status."""
        tests_dir = Path(options.tests_dir)
        start = time.time()
        test_files = RouterShellTestRunner._discover(tests_dir, options.pattern)
        if not test_files:
            print(f"No test files found matching {options.pattern!r} in {tests_dir}.")
            return 1

        results: list[TestResult] = []
        for path in test_files:
            print(f"Running {path}...")
            result = RouterShellTestRunner._run_file(path, options.verbose, options.failfast)
            results.append(result)
            if options.failfast and not result.success:
                break

        summary = TestSummary(
            total_files=len(results),
            successful_files=sum(1 for result in results if result.success),
            failed_files=sum(1 for result in results if not result.success),
            total_tests=sum(result.tests_run for result in results),
            total_failures=sum(result.failures for result in results),
            total_errors=sum(result.errors for result in results),
            total_skipped=sum(result.skipped for result in results),
            total_duration=time.time() - start,
            results=results,
        )

        print("\nTest summary")
        print(f"Files: {summary.successful_files}/{summary.total_files} passed")
        passed_tests = summary.total_tests - summary.total_failures - summary.total_errors
        print(f"Tests: {passed_tests}/{summary.total_tests} passed")
        print(f"Failures: {summary.total_failures}")
        print(f"Errors: {summary.total_errors}")
        print(f"Skipped: {summary.total_skipped}")
        print(f"Duration: {summary.total_duration:.3f}s")

        if options.json_report:
            RouterShellTestRunner._write_json(summary, Path(options.output_dir))

        return 0 if summary.failed_files == 0 else 1


def main() -> int:
    """Run the RouterShell unittest runner."""
    parser = RouterShellTestRunner._build_parser()
    try:
        return RouterShellTestRunner.run(parser.parse_args())
    except KeyboardInterrupt:
        print("Test execution interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

# FILE: tools/services/dhcp_client_simulation.sh
#!/usr/bin/env bash

# Function to display script usage
display_usage() {
    echo "Usage: $0 -n <num_interfaces>"
    echo "Example: $0 -n 10"
}

# Initialize default values
num_interfaces=""

# Parse command-line options
while getopts ":n:" opt; do
    case $opt in
        n)
            num_interfaces="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            display_usage
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument."
            display_usage
            exit 1
            ;;
    esac
done

# Check for the required option
if [ -z "$num_interfaces" ]; then
    echo "Missing required option."
    display_usage
    exit 1
fi

# Validate user input
if ! [[ "$num_interfaces" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid input. Please enter a positive integer for the number of loopback interfaces."
    display_usage
    exit 1
fi

# Create loopback interfaces based on user input
for ((i = 1; i <= num_interfaces; i++)); do
    ip link add lo$i type dummy
done

# Activate loopback interfaces
for ((i = 1; i <= num_interfaces; i++)); do
    ip link set lo$i up
done

# Install DHCP client if not already installed
if ! command -v dhclient &> /dev/null; then
    echo "Installing DHCP client..."
    sudo apt-get update
    sudo apt-get install -y isc-dhcp-client
fi

# Configure DHCP on loopback interfaces
for ((i = 1; i <= num_interfaces; i++)); do
    dhclient lo$i
done

# Display the configured IP addresses
ip address show

# FILE: tools/services/dhcp_server_options.sh
#!/usr/bin/env bash

# Default values for DHCP settings
interface="enx3c8cf8f943a2"
subnet="172.16.0.0"
netmask="255.255.255.0"
range_start="172.16.0.2"
range_end="172.16.0.253"
gateway="172.16.0.1"
dns_servers="8.8.8.8"
enable_dhcp=false
disable_dhcp=false

# Function to show script usage
show_usage() {
    echo "Usage: $0 [-e] [-d] [-i interface] [-s subnet] [-m netmask] [-r range_start] [-R range_end] [-g gateway] [-n dns_servers]"
    echo "  -e               Enable DHCP server"
    echo "  -d               Disable DHCP server"
    echo "  -i interface     Network interface to listen on (default: ${interface})"
    echo "  -s subnet        Subnet (default: ${subnet})"
    echo "  -m netmask       Netmask (default: ${netmask})"
    echo "  -r range_start   IP address range start (default: ${range_start})"
    echo "  -R range_end     IP address range end (default: ${range_end})"
    echo "  -g gateway       Gateway IP address (default: ${gateway})"
    echo "  -n dns_servers   DNS server(s) (default: ${dns_servers})"
    exit 1
}

# Parse command-line options
while getopts "edi:s:m:r:R:g:n:" opt; do
    case $opt in
        e)
            enable_dhcp=true
            ;;
        d)
            disable_dhcp=true
            ;;
        i)
            interface="$OPTARG"
            ;;
        s)
            subnet="$OPTARG"
            ;;
        m)
            netmask="$OPTARG"
            ;;
        r)
            range_start="$OPTARG"
            ;;
        R)
            range_end="$OPTARG"
            ;;
        g)
            gateway="$OPTARG"
            ;;
        n)
            dns_servers="$OPTARG"
            ;;
        \?)
            show_usage
            ;;
    esac
done

# Install DHCP Server if not already installed
if ! dpkg -l | grep -q "isc-dhcp-server"; then
    echo "Installing ISC DHCP Server..."
    apt-get update
    apt-get install -y isc-dhcp-server
fi

# Configuration file for DHCPv4
dhcp_config="/etc/dhcp/dhcpd.conf"

# Enable DHCP server
enable_dhcp_server() {
    # Create DHCP configuration file
    cat <<EOL > "$dhcp_config"
    subnet $subnet netmask $netmask {
        range $range_start $range_end;
        option routers $gateway;
        option domain-name-servers $dns_servers;
        default-lease-time 600;
        max-lease-time 7200;
    }
EOL
    # Configure the DHCP server to listen on the specified interface
    echo "INTERFACESv4=\"$interface\"" >> /etc/default/isc-dhcp-server

    # Start the DHCP server
    systemctl start isc-dhcp-server

    # Enable the DHCP server to start on boot
    systemctl enable isc-dhcp-server

    echo "DHCPv4 server enabled for $interface."
}

# Disable DHCP server
disable_dhcp_server() {
    # Stop the DHCP server
    systemctl stop isc-dhcp-server

    # Disable the DHCP server from starting on boot
    systemctl disable isc-dhcp-server

    # Remove the DHCP configuration file
    rm -f "$dhcp_config"

    echo "DHCPv4 server disabled for $interface."
}

# Enable or disable DHCP server based on command-line options
if $enable_dhcp; then
    enable_dhcp_server
elif $disable_dhcp; then
    disable_dhcp_server
else
    show_usage
fi

# FILE: tools/services/uninstall_dnsmasq.sh
#!/usr/bin/env bash

# Stop Dnsmasq
sudo systemctl stop dnsmasq

# Remove Dnsmasq
sudo systemctl disable dnsmasq

# Uninstall Dnsmasq
sudo apt remove dnsmasq

# Purge configuration files
sudo apt purge dnsmasq

# Remove any residual packages
sudo apt autoremove

# Reload systemd
sudo systemctl daemon-reload

# Clean up
sudo rm -rf /etc/dnsmasq.d /etc/dnsmasq.conf /var/lib/misc/dnsmasq.leases

echo "Dnsmasq stopped, removed, and uninstalled."

# FILE: tools/services/uninstall_kea_server.sh
#!/usr/bin/env bash

# Stop KEA DHCP Server
sudo systemctl stop kea-dhcp4-server
sudo systemctl stop kea-dhcp6-server

# Remove KEA DHCP Server
sudo systemctl disable kea-dhcp4-server
sudo systemctl disable kea-dhcp6-server

# Uninstall KEA DHCP Server
sudo apt remove kea-dhcp4-server kea-dhcp6-server

# Purge configuration files
sudo apt purge kea-dhcp4-server kea-dhcp6-server

# Remove any residual packages
sudo apt autoremove

# Reload systemd
sudo systemctl daemon-reload

# Clean up
sudo rm -rf /etc/kea /var/lib/kea

echo "KEA DHCP Server stopped, removed, and uninstalled."

