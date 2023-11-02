
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

            # Debug line to log the section
            self.log.debug("Section:")
            self.log.debug(section)

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
                self.log.debug("Line:")
                self.log.debug(line)
                if "bus info:" in line:
                    self.log.debug("Found 'bus info:'")
                    interface_data['Bus Info'] = line.split("bus info:")[1].strip()
                elif "logical name:" in line:
                    self.log.debug("Found 'logical name:'")
                    interface_data['Logical Name'] = line.split("logical name:")[1].strip()
                elif "serial:" in line:
                    self.log.debug("Found 'serial:'")
                    interface_data['Serial'] = line.split("serial:")[1].strip()
                elif "configuration:" in line:
                    self.log.debug("Found 'configuration:'")
                    configuration = line.split("configuration:")[1].strip()
                    if "pci@" in interface_data['Bus Info'] and "wireless" in configuration.lower():
                        self.log.debug("Detected 'pci@' and 'wireless'")
                        interface_data['Type'] = "Wireless"
                elif "capacity:" in line:
                    self.log.debug("Found 'capacity:'")
                    interface_data['Capacity'] = line.split("capacity:")[1].strip()

            # Debug line to log the interface data
            self.log.debug("Interface Data:")
            self.log.debug(interface_data)

            # Determine the interface type based on bus info
            if "usb@" in interface_data['Bus Info']:
                self.log.debug("Detected 'usb@'")
                interface_data['Type'] = "USB-Ethernet"
            elif "pci@" in interface_data['Bus Info'] and "Wireless" not in interface_data['Type']:
                self.log.debug("Detected 'pci@' and not 'Wireless'")
                interface_data['Type'] = "PCI-Ethernet"

            # Append the interface information to the list
            interface_info.append(interface_data)

        # Debug line to log the final interface_info list
        self.log.debug("Interface Info:")
        self.log.debug(interface_info)

        return interface_info
