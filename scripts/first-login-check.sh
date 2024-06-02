#!/usr/bin/env bash


function toShell() {
    /usr/bin/env bash
}

# Path to a file that indicates the script has already been run
FLAG_DIR="/var/lib/first-boot"
FLAG_FILE="$FLAG_DIR/first_boot_done"

mkdir -p $FLAG_DIR

# Check if the script has already been run
if [ -f "$FLAG_FILE" ]; then

    # TODO Add a bypass flag at for Debug-Version
    toShell

    # /etc/routershell/router-shell.sh

    exit 0
fi

echo "Initial Login, MUST create new username and password."

# Prompt for new username
read -p "Enter new username: " new_username

# Create the new user
adduser $new_username
passwd $new_username

# Add new user to sudoers file
# usermod -aG sudo $new_username

echo "dev01 ALL=(ALL:ALL) ALL" | sudo tee -a /etc/sudoers

# Mark the script as run
touch $FLAG_FILE

echo "Initial setup is complete. Please log in as $new_username."

# Exit script
exit 0
