#!/usr/bin/env bash

# Set project root and update PYTHONPATH
export ROUTERSHELL_PROJECT_ROOT="${PWD}" 
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

# Function to display usage information
usage() {
    echo "Usage: $0 [--factory-reset]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -f|--factory-reset)
            factory_reset=true
            break
            ;;

        -h|--help)
            echo "Invalid option: -$key."
            usage
            ;;
    esac
done

# Perform factory reset if the option is specified
if [ "$factory_reset" = true ]; then
    echo "Performing factory reset..."
    
    factory_reset_script="${ROUTERSHELL_PROJECT_ROOT}/src/factory-reset.py"

    if [ ! -x "$factory_reset_script" ]; then
        echo "Error: $factory_reset_script does not exist or is not executable."
        exit 1
    fi
    "$factory_reset_script"
    exit 0
fi

# Determine the current user
current_user="$(whoami)"
if [ -z "$current_user" ]; then
    echo "Error: Could not determine the current user."
    exit 1
fi

# Create the directory with error checking
log_dir="/tmp/log"
if ! mkdir -m 775 -p "$log_dir"; then
    echo "Error: Could not create directory $log_dir."
    exit 1
fi

# Set the owner and group to the current user with error checking
if ! sudo chown "$current_user":"$current_user" "$log_dir"; then
    echo "Error: Could not set owner and group for $log_dir."
    exit 1
fi

# Check if the main.py script exists and is executable
main_script="${ROUTERSHELL_PROJECT_ROOT}/src/main.py"
if [ ! -x "$main_script" ]; then
    echo "Error: $main_script does not exist or is not executable."
    exit 1
fi

# Execute the main.py script
if ! "$main_script"; then
    echo "Error: Execution of $main_script failed."
    exit 1
fi
