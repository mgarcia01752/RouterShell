#!/bin/bash

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
