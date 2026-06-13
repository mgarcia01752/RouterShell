#!/usr/bin/env bash

# Function to display a numbered list of network interfaces with their current state
display_interfaces() {
  echo "Available Network Interfaces:"
  echo -e "Index\tInterface\tState"
  interfaces=($(ifconfig -s -a | awk '{print $1}' | sed -n '2,$p'))
  for ((i=0; i<${#interfaces[@]}; i++)); do
    interface="${interfaces[$i]}"
    state=$(ifconfig "$interface" | grep -q "UP" && echo "UP" || echo "DOWN")
    echo -e "$i\t$interface\t$state"
  done
}

# Function to toggle the selected network interface
toggle_interface() {
  read -p "Enter the number of the interface to toggle: " choice

  # Check if the input is a valid number
  if [[ ! $choice =~ ^[0-9]+$ ]]; then
    echo "Invalid input. Please enter a valid number."
    return
  fi

  # Check if the selected number is within the range of available interfaces
  if ((choice < 0 || choice >= ${#interfaces[@]})); then
    echo "Invalid interface number. Please select a number from the list."
    return
  fi

  selected_interface="${interfaces[$choice]}"

  # Check if the selected interface is currently up or down and toggle it
  if ifconfig "$selected_interface" | grep -q "UP"; then
    echo "Disabling interface $selected_interface..."
    sudo ifconfig "$selected_interface" down
    echo "Interface $selected_interface is now disabled."
  else
    echo "Enabling interface $selected_interface..."
    sudo ifconfig "$selected_interface" up
    echo "Interface $selected_interface is now enabled."
  fi
}

# Main script
clear
display_interfaces
toggle_interface
