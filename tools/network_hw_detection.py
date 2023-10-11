#!/usr/bin/env python3

import subprocess
from tabulate import tabulate

def detect_network_hardware():
    interface_info = []

    try:
        # Run the 'lshw -c network' command and capture the output
        network_info = subprocess.check_output(['sudo', 'lshw', '-c', 'network'], text=True)

        # Split the output into sections for each network interface
        sections = network_info.split('*-network')

        for section in sections[1:]:
            lines = section.strip().split('\n')

            # Initialize a dictionary to store information for this interface
            interface_data = {
                'Logical Name': "N/A",
                'Bus Info': "N/A",
                'Serial': "N/A",
                'Capacity': "N/A",
                'Type': 'Unknown'
            }

            # Parse the lines for relevant information
            for line in lines:
                if "bus info:" in line:
                    interface_data['Bus Info'] = line.split("bus info:")[1].strip()
                elif "logical name:" in line:
                    interface_data['Logical Name'] = line.split("logical name:")[1].strip()
                elif "serial:" in line:
                    interface_data['Serial'] = line.split("serial:")[1].strip()
                elif "configuration:" in line:
                    configuration = line.split("configuration:")[1].strip()
                    if "pci@" in interface_data['Bus Info'] and "wireless" in configuration.lower():
                        interface_data['Type'] = "Wireless"
                elif "capacity:" in line:
                    interface_data['Capacity'] = line.split("capacity:")[1].strip()

            # Determine the interface type based on bus info
            if "usb@" in interface_data['Bus Info']:
                interface_data['Type'] = "USB-Ethernet"
            elif "pci@" in interface_data['Bus Info'] and "Wireless" not in interface_data['Type']:
                interface_data['Type'] = "PCI-Ethernet"

            # Append the interface information to the list
            interface_info.append(interface_data)

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return interface_info

if __name__ == "__main__":
    detected_interfaces = detect_network_hardware()

    # Display the interface information in a tabular format
    headers = ['Logical Name', 'Bus Info', 'Serial', 'Capacity', 'Type']
    table_data = [[
        interface['Logical Name'],
        interface['Bus Info'],
        interface['Serial'],
        interface['Capacity'],
        interface['Type']
    ] for interface in detected_interfaces]

    print(tabulate(table_data, headers, tablefmt='simple'))
