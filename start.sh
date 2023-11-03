#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    # Check if pip3 is installed
    if ! command -v pip3 &>/dev/null; then
        echo "pip3 is not installed. Please install it before running this script."
        exit 1
    fi

    # Install Python packages if not running as root
    pip3_packages=("tabulate" "prettytable" "argcomplete" "cmd2")
    for package in "${pip3_packages[@]}"; do
        if pip3 show "$package" &>/dev/null; then
            echo
        else
            pip3 install "$package"
            echo "$package installed successfully."
        fi
    done
else
    echo "Please do not run this script as root. Run it as a regular user."
    exit 1
fi

ROUTERSHELL_PROJECT_ROOT="${PWD}"
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

# Determine the current user
current_user="$(whoami)"

# Create the directory
mkdir -m 775 -p /tmp/log

# Set the owner and group to the current user
sudo chown "$current_user":"$current_user" /tmp/log

src/main.py
