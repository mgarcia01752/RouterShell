#!/bin/bash

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
