#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    # Check if pip3 is installed
    if ! command -v pip3 &>/dev/null; then
        echo "pip3 is not installed. Please install it before running this script."
        exit 1
    fi

    # Install Python packages if not running as root
    pip3_packages=("tabulate" "prettytable" "argcomplete" "cmd2" "jc")
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
