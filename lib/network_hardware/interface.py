
import logging
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.run_commands import RunCommand


class NetworkHardware(RunCommand):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().HARDWARE_NETWORK)
        pass
    
    def hardware_memory(self):
        pass
    
    def hardware_network(self):
        interface_info = []

        # Run the 'lshw -c network' command and capture the output
        network_info = self.run(['lshw', '-c', 'network'])

        # Split the output into sections for each network interface
        sections = network_info.stdout.split('*-network')

        for section in sections[1:]:
            lines = section.strip().split('\n')

        # Run the 'lshw -c network' command and capture the outputfree -h
        network_info = self.run(['lshw', '-c', 'network'])

        # Split the output into sections for each network interface
        sections = network_info.stdout.split('*-network')

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

            return interface_info