#!/bin/bash

# Default values
ssd_device=""
check_local_drive=true

# Parse command-line options
while getopts "d:n" opt; do
  case $opt in
    d)
      ssd_device="/dev/$OPTARG"
      ;;
    n)
      check_local_drive=false
      ;;
    \?)
      echo "Usage: $0 -d <ssd_device> [-n]"
      exit 1
      ;;
  esac
done

# Check if the SSD device is specified
if [ -z "$ssd_device" ]; then
    echo "Error: SSD device not specified."
    exit 1
fi

# Check if the specified device exists
if [ ! -b "$ssd_device" ]; then
    echo "Error: SSD device not found."
    exit 1
fi

# Check if the specified device is a local drive (optional)
if $check_local_drive; then
    local_drive=$(df -P "$ssd_device" | awk 'NR==2 {print $1}')
    if [ "$ssd_device" == "$local_drive" ]; then
        echo "Error: Attempting to format a local drive. Use the -n option to skip this check."
        exit 1
    fi
fi

# Unmount partitions
sudo umount "${ssd_device}1" 2>/dev/null

# Partition the SSD using fdisk
sudo fdisk "$ssd_device" <<EOF
o
n
p
1


w
EOF

# Unmount partitions again to be sure
sudo umount "${ssd_device}1" 2>/dev/null

# Create a file system on the partition
sudo mkfs.ext4 "${ssd_device}1"

# Eject the device using udisksctl
udisksctl unmount --block-device "$ssd_device" && udisksctl eject --block-device "$ssd_device"

echo "Single partition on $ssd_device created successfully, formatted, and ejected."
