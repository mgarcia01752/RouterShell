import json
import logging

from tabulate import tabulate


from lib.network_manager.bridge import Bridge


class BridgeShow(Bridge):
    """Command set for showing Bridge-Show-Command"""

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg

    def bridge(self, arg=None):
        self.get_bridge()

    def show_bridges(self, args=None):
        # Run the 'ip -json link show type bridge' command and capture its output
        result = self.run(['ip', '-json', 'link', 'show', 'type', 'bridge'])

        # Check if the command was successful
        if result.exit_code != 0:
            print("Error executing 'ip -json link show type bridge'.")
            return

        # Parse the JSON output
        json_data = result.stdout

        # Parse the JSON data into a list of bridge interfaces
        bridge_data = json.loads(json_data)

        # Prepare data for tabulation
        table_data = []

        # Check if bridge_data is a list
        if isinstance(bridge_data, list):
            for info in bridge_data:
                bridge_name = info.get("ifname", "")
                ether = info.get("address", "")
                flags = info.get("flags", [])
                state = "UP" if "UP" in flags else "DOWN"

                table_data.append([bridge_name, ether, state])
        else:
            bridge_name = bridge_data.get("ifname", "")
            ether = bridge_data.get("address", "")
            flags = bridge_data.get("flags", [])
            state = "UP" if "UP" in flags else "DOWN"

            table_data.append([bridge_name, ether, state])

        # Define headers
        headers = ["Bridge Name", "ether", "State"]

        # Display the table using tabulate
        table = tabulate(table_data, headers, tablefmt="simple")

        print(table)
