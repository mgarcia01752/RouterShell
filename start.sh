#!/usr/bin/env bash

ROUTERSHELL_PROJECT_ROOT="${PWD}"
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

# Determine the current user
current_user="$(whoami)"

# Create the directory
mkdir -m 775 -p /tmp/log

# Set the owner and group to the current user
sudo chown "$current_user":"$current_user" /tmp/log

# Check if there are any arguments
if [ "$#" -eq 0 ]; then
    # No arguments provided, run main.py
    src/main.py
else
    # Arguments provided, run test.py
    src/test.py "$@"
fi
