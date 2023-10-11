import json

class NatPoolDB:
    # Class-level dictionary to store NAT pool configurations
    nat_pool_db = {}

    @classmethod
    def create_nat_pool(cls, pool_name: str) -> None:
        """
        Create a NAT pool with the specified pool name and initialize it in the database.

        Args:
            pool_name (str): The name of the NAT pool to create.
        """
        # Initialize the NAT pool in the database with empty inside_interfaces and outside_interface
        cls.nat_pool_db[pool_name] = {
            "inside_interfaces": [],
            "outside_interface": None
        }

    def add_inside_interface(self, pool_name: str, interface_name: str) -> None:
        """
        Add an inside interface to the NAT pool.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface.
        """
        # Check if the NAT pool exists in the database, if not, initialize it
        if pool_name not in self.nat_pool_db:
            self.create_nat_pool(pool_name)
        
        # Add the inside interface to the NAT pool
        self.nat_pool_db[pool_name]["inside_interfaces"].append(interface_name)

    def set_outside_interface(self, pool_name: str, interface_name: str) -> None:
        """
        Set the outside interface for the NAT pool.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the outside interface.
        """
        
        # Check if the NAT pool exists in the database, if not, initialize it
        if pool_name not in self.nat_pool_db:
            if not self.create_nat_pool(pool_name):
                print(f"Error: Failed to create NAT pool with name '{pool_name}'.")
                return

        try:
            # Set the outside interface for the NAT pool
            self.nat_pool_db[pool_name]["outside_interface"] = interface_name
            print(f"Outside interface set to '{interface_name}' for NAT pool '{pool_name}'.")
        except KeyError:
            print(f"Error: NAT pool '{pool_name}' does not exist in the database.")

    def delete_inside_interface(self, pool_name: str, interface_name: str) -> bool:
        """
        Delete an inside interface from the NAT pool.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface to delete.

        Returns:
            bool: True if the interface was successfully deleted, False otherwise.
        """
        if pool_name in self.nat_pool_db and interface_name in self.nat_pool_db[pool_name]["inside_interfaces"]:
            self.nat_pool_db[pool_name]["inside_interfaces"].remove(interface_name)
            return True
        else:
            return False

    def delete_nat_pool(self, pool_name: str) -> None:
        """
        Delete the entire NAT pool.

        Args:
            pool_name (str): The name of the NAT pool to delete.
        """
        if pool_name in self.nat_pool_db:
            del self.nat_pool_db[pool_name]

    def reset_db(self) -> None:
        """
        Reset the NAT pool database.

        This method clears all NAT pool configurations in the database by
        setting the `nat_pool_db` dictionary to an empty dictionary.

        Returns:
        None
        """
        self.nat_pool_db = {}

    def save_to_db(self, nat_pool_name: str) -> None:
        """
        Save the current NAT pool configuration to the database.

        Args:
            nat_pool_name (str): The name of the NAT pool.
        """
        # Save the NAT pool configuration to the database
        # (already updated within the add_inside_interface and set_outside_interface methods)

    def to_json(self, pool_name: str = None) -> str:
        """
        Convert NAT pool configuration to JSON format.

        Args:
            pool_name (str, optional): The name of the NAT pool. If not specified, the entire database will be included.

        Returns:
            str: JSON representation of NAT pool configuration.
        """
        if pool_name:
            if pool_name in self.nat_pool_db:
                data = self.nat_pool_db[pool_name]
                data["name"] = pool_name
                return json.dumps(data, indent=4)
            else:
                return json.dumps({"error": "NAT pool not found."}, indent=4)
        else:
            # If no pool_name is specified, return the entire database
            return json.dumps(self.nat_pool_db, indent=4)

    @classmethod
    def get_pool(cls, pool_name: str) -> 'NatPoolDB':
        """
        Retrieve a NAT pool from the database based on its name.

        Args:
            pool_name (str): The name of the NAT pool to retrieve.

        Returns:
            NatPoolDB or None: The retrieved NAT pool or None if not found.
        """
        if pool_name in cls.nat_pool_db:
            pool_info = cls.nat_pool_db[pool_name]
            nat_pool = cls()
            nat_pool.name = pool_name
            nat_pool.inside_interfaces = pool_info["inside_interfaces"]
            nat_pool.outside_interface = pool_info["outside_interface"]
            return nat_pool
        else:
            return None

    @classmethod
    def get_outside_interface(cls, pool_name: str) -> str:
        """
        Get the outside interface associated with the NAT pool by its name.

        Args:
            pool_name (str): The name of the NAT pool.

        Returns:
            str or None: The outside interface name or None if not found.
        """
        if pool_name in cls.nat_pool_db:
            return cls.nat_pool_db[pool_name].get("outside_interface", None)
        else:
            return None

    def __str__(self) -> str:
        return f"Name: {self.name}, Inside Interfaces: {self.inside_interfaces}, Outside Interface: {self.outside_interface}"
