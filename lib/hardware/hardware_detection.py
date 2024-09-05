
import json
import logging

from tabulate import tabulate
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.common.run_commands import RunCommand


class HardwareDetection(RunCommand):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().HARDWARE_NETWORK)
        pass
    
    def hardware_cpu(self):
        
        def extract_field(data, field_name):
            for item in data:
                if item['field'] == field_name:
                    return item['data']
            return "N/A"

        try:
            # Run the 'lscpu -J' command and capture the output
            result = self.run(['lscpu', '-J'],)
            lscpu_json = result.stdout

            # Load the JSON data
            data = json.loads(lscpu_json)['lscpu']

            # Extract relevant information and create a table
            architecture = extract_field(data, "Architecture:")
            cpu_count = extract_field(data, "CPU(s):")
            vendor_id = extract_field(data, "Vendor ID:")

            model_name = extract_field(data, "Model name:")
            cpu_family = extract_field(data, "CPU family:")
            model = extract_field(data, "Model:")
            thread_per_core = extract_field(data, "Thread(s) per core:")
            core_per_socket = extract_field(data, "Core(s) per socket:")
            socket_count = extract_field(data, "Socket(s):")
            cpu_max_mhz = extract_field(data, "CPU max MHz:")
            cpu_min_mhz = extract_field(data, "CPU min MHz:")
            bogo_mips = extract_field(data, "BogoMIPS:")

            virtualization = extract_field(data, "Virtualization:")

            table = [
                ["Model Name", model_name],    
                ["Vendor ID", vendor_id],                    
                ["Model", model],
                ["Architecture", architecture],
                ["CPU(s)", cpu_count],
                ["CPU Family", cpu_family],
                ["Thread(s) per Core", thread_per_core],
                ["Core(s) per Socket", core_per_socket],
                ["Socket(s)", socket_count],
                ["CPU Min/Max MHz", f'{cpu_min_mhz}/{cpu_max_mhz}'],
                ["BogoMIPS", bogo_mips],
                ["Virtualization", virtualization],
            ]

            # Generate the tabulated summary
            summary = tabulate(table, headers=["CPU", "Info"], tablefmt="simple")

            return summary

        except Exception as e:
            return f"Error: {str(e)}"        
            
    def hardware_network(self):
        interface_info = []

        network_info = self.run(['lshw', '-c', 'network'])
        
        sections = network_info.stdout.split('*-network')

        for section in sections[1:]:
            lines = section.strip().split('\n')

            # Debug line to log the section
            self.log.debug("Section:")
            self.log.debug(section)

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

            headers = ['Logical Name', 'Bus Info', 'Serial', 'Capacity', 'Type']
            table_data = [[
                interface['Logical Name'],
                interface['Bus Info'],
                interface['Serial'],
                interface['Capacity'],
                interface['Type']
            ] for interface in interface_info]

        return tabulate(table_data, headers, tablefmt='simple')
