#!/usr/bin/env bash

function toShell() {
    /usr/bin/env bash
}

function changeRootShellToNologin() {
    echo "Changing root shell to /sbin/nologin"
    sudo sed -i 's#^root:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:/bin/bash#root:x:0:0:root:/root:/sbin/nologin#' /etc/passwd
}

# Function to configure passwordless sudo access for a user
function configurePasswordlessSudo() {
    local username="$1"
    local sudoers_file="/etc/sudoers.d/$username"

    # Create a custom sudoers file for the user
    echo "$username ALL=(ALL) NOPASSWD: ALL" | sudo tee "$sudoers_file" > /dev/null

    # Validate the sudoers file syntax
    if sudo visudo -cf "$sudoers_file"; then
        echo "Sudo configuration for $username was successful."
    else
        echo " ERROR: Sudo configuration for $username failed. Please check the sudoers file."
        exit 1
    fi
}

# Directory and file to indicate whether the script has been run
FLAG_DIR="/var/lib/first-boot"
FLAG_FILE="$FLAG_DIR/first_boot_done"

# Create the directory if it doesn't exist
mkdir -p "$FLAG_DIR"

# Check if the script has already been run
if [ -f "$FLAG_FILE" ]; then
    sudo /usr/lib/routershell/router-shell.sh
    exit 0
fi

echo "Initial Login: You must create a new username and password."

# Prompt for a new username
read -p "Enter the new username: " new_username

# Create the new user and set their password
adduser "$new_username"

# Add the new user to the sudo group
sudo usermod -aG sudo "$new_username"

# Configure passwordless sudo access for the new user
configurePasswordlessSudo "$new_username"

# Indicate that the script has been run
touch "$FLAG_FILE"

changeRootShellToNologin

echo "Initial setup is complete. Please log in as $new_username."

# Exit the script
exit 0
