#!/usr/bin/env bash

# Function to clear __pycache__ directories recursively
clear_pycache() {
    local dir_path="$1"

    # Find and delete all __pycache__ directories
    find "$dir_path" -type d -name "__pycache__" -exec rm -r {} +

    echo "All __pycache__ directories have been deleted from $dir_path."
}

# Check if the directory path is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/your/directory"
    exit 1
fi

# Call the function with the provided directory path
clear_pycache "$1"
