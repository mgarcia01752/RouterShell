import json
import subprocess
from tabulate import tabulate

def extract_field(data, field_name):
    for item in data:
        if item['field'] == field_name:
            return item['data']
    return "N/A"

def create_tabulated_summary():
    try:
        # Run the 'lscpu -J' command and capture the output
        result = subprocess.run(['lscpu', '-J'], capture_output=True, text=True, check=True)
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

# Example usage:
summary = create_tabulated_summary()
print(summary)
