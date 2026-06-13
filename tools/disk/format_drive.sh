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
