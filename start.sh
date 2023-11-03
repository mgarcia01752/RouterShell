#!/bin/bash

ROUTERSHELL_PROJECT_ROOT="${PWD}"
export PYTHONPATH="${PYTHONPATH}:${ROUTERSHELL_PROJECT_ROOT}:${ROUTERSHELL_PROJECT_ROOT}/src:${ROUTERSHELL_PROJECT_ROOT}/lib:${ROUTERSHELL_PROJECT_ROOT}/test"

# Determine the current user
current_user="$(whoami)"

# Create the directory
mkdir -m 775 -p /tmp/log

# Set the owner and group to the current userq  
sudo chown "$current_user":"$current_user" /tmp/log

src/main.py
# src/test.py