#!/bin/bash

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
