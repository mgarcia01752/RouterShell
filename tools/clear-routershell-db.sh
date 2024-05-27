#!/bin/bash

# Prompt the user for confirmation
read -p "Are you sure you want to delete the router-shell db file (routershell.db)? (Y|y/n) " -n 1 -r
echo

# Check if the user's response is Y or y
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Find the routershell.db file in the relative path
    db_files=$(find . -type f -name "routershell.db")

    # Check if there is exactly one db file found
    if [ $(echo "$db_files" | wc -l) -eq 1 ]
    then
        echo "Deleting the file..."
        rm "$db_files"
    elif [ -z "$db_files" ]
    then
        echo "No routershell.db file found."
    else
        echo "Multiple routershell.db files found. Please ensure there is only one file."
    fi
else
    echo "Operation cancelled."
fi
