import json
from typing import List, Optional

class InterfaceConfigDB:
    """A class to manage interface configurations in a static dictionary-based database.

    This class allows you to store and retrieve interface configurations where the
    interface name serves as the main lookup key, and each line within an interface
    block is stored as a unique key.

    Attributes:
        db (dict): A dictionary to store interface configurations.

    """

    if_db: dict = {}

    @classmethod
    def add_interface(cls, interface_name: str) -> None:
        """Add a new interface entry to the database.

        Args:
            interface_name (str): The name of the interface to be added.

        """
        cls.if_db[interface_name] = []

    @classmethod
    def add_line_to_interface(cls, interface_name: str, line: str) -> None:
        """Add an individual line to an existing interface entry in the database.

        Args:
            interface_name (str): The name of the interface.
            line (str): The configuration line to be added.

        """
        if interface_name in cls.if_db:
            cls.if_db[interface_name].append(line)

    @classmethod
    def get_interface_config(cls, interface_name: str) -> List[str]:
        """Retrieve the configuration of a specific interface.

        Args:
            interface_name (str): The name of the interface to retrieve.

        Returns:
            List[str]: A list of configuration lines for the specified interface.
                An empty list is returned if the interface is not found.

        """
        return cls.if_db.get(interface_name, [])

    @classmethod
    def get_all_configs(cls) -> dict:
        """Retrieve all interface configurations.

        Returns:
            dict: A dictionary where keys are interface names, and values are lists
                of configuration lines for each interface.

        """
        return cls.if_db

    @classmethod
    def to_json(cls) -> str:
        """Serialize the interface configurations to JSON format.

        Returns:
            str: A JSON string representing the interface configurations.

        """
        return cls.if_db

    @classmethod
    def parse_config(cls, config_data: str) -> None:
        """Parse and store configuration data in the database.

        Args:
            config_data (str): The configuration data to be parsed and stored.

        """
        # Split the configuration data into individual lines
        lines = config_data.split('\n')

        # Initialize variables to track the current interface name and lines
        current_interface: Optional[str] = None
        current_lines: List[str] = []

        # Parse the configuration data and add it to the database
        for line in lines:
            line = line.strip()
            if line.startswith("interface "):
                # New interface block, save the previous one if it exists
                if current_interface:
                    cls.add_interface(current_interface)
                    for config_line in current_lines:
                        cls.add_line_to_interface(current_interface, config_line)
                # Get the new interface name
                current_interface = line.split(" ")[1]
                current_lines = []
            elif line == "end":
                # End of interface block, save it
                if current_interface:
                    for config_line in current_lines:
                        cls.add_line_to_interface(current_interface, config_line)
            else:
                # Regular configuration line
                current_lines.append(line)
