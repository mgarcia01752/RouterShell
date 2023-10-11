from typing import Dict, Optional, List

class VLANDatabase:
    """
    A class for managing VLANs in a database.
    """

    # Class-level attribute to store VLAN database
    vlan_db: Dict[str, Dict[str, any]] = {"vlans": {}}

    @classmethod
    def add_vlan(cls, vlan_id:int, vlan_name:str=None, description:str=None, ports:List[str]=None):
        """
        Add a VLAN to the database.

        Args:
            vlan_id (int): The VLAN ID.
            vlan_name (str or None): The VLAN name. If None, a default name is generated.
            description (str): A description of the VLAN.
            ports (List[int]): List of port numbers associated with the VLAN.

        Raises:
            ValueError: If a VLAN with the same ID or name already exists.
        """
        str_vlan_id = str(vlan_id)
        
        # Check if the VLAN ID already exists
        if str_vlan_id in cls.vlan_db["vlans"]:
            raise ValueError(f"VLAN with ID {vlan_id} already exists.")
        
        # Check if the VLAN name already exists
        for vlan_data in cls.vlan_db["vlans"].values():
            if vlan_name and vlan_data["name"] == vlan_name:
                raise ValueError(f"VLAN with name '{vlan_name}' already exists.")
        
        # Generate a default VLAN name if vlan_name is None
        if vlan_name is None:
            vlan_name = f"vlan{vlan_id}"
        
        cls.vlan_db["vlans"][str_vlan_id] = {
            "name": vlan_name,
            "description": description,
            "ports": ports
        }

    @classmethod
    def vlan_exists(cls, vlan_id: int) -> bool:
        """
        Check if a VLAN with a given VLAN ID exists.

        Args:
            vlan_id (int): The VLAN ID to check.

        Returns:
            bool: True if the VLAN exists, False otherwise.
        """
        return str(vlan_id) in cls.vlan_db["vlans"]
    
    @classmethod
    def get_vlan_name(cls, vlan_id: int) -> str:
        """
        Get the name of a VLAN by VLAN ID.

        Args:
            vlan_id (int): The VLAN ID.

        Returns:
            str or None: The name of the VLAN, or None if VLAN not found.
        """
        vlan_data = cls.vlan_db["vlans"].get(str(vlan_id))
        if vlan_data is not None:
            return vlan_data.get("name")
        return None

    @classmethod
    def update_vlan_name(cls, vlan_id: int, vlan_name: str):
        """
        Update the name of a VLAN by VLAN ID.

        Args:
            vlan_id (int): The VLAN ID to be updated.
            vlan_name (str): The new VLAN name.

        Raises:
            KeyError: If the specified VLAN ID does not exist in the database.
        """
        str_vlan_id = str(vlan_id)
        if str_vlan_id not in cls.vlan_db["vlans"]:
            raise KeyError(f"VLAN with ID {vlan_id} does not exist.")
        
        cls.vlan_db["vlans"][str_vlan_id]["name"] = vlan_name       

    @classmethod
    def update_vlan_description(cls, vlan_id: int, vlan_description: str):
        """
        Update the description of a VLAN by VLAN ID.

        Args:
            vlan_id (int): The VLAN ID to be updated.
            vlan_description (str): The new VLAN description.

        Raises:
            KeyError: If the specified VLAN ID does not exist in the database.
        """
        str_vlan_id = str(vlan_id)
        if str_vlan_id not in cls.vlan_db["vlans"]:
            raise KeyError(f"VLAN with ID {vlan_id} does not exist.")
        
        cls.vlan_db["vlans"][str_vlan_id]["description"] = vlan_description       
    
    @classmethod
    def add_ports_to_vlan(cls, vlan_id: int, ports_to_add: List[int]):
        """
        Add ports to an existing VLAN.

        Args:
            vlan_id (int): The VLAN ID to which ports will be added.
            ports_to_add (List[int]): List of port numbers to add to the VLAN.

        Raises:
            KeyError: If the specified VLAN ID does not exist in the database.
        """
        str_vlan_id = str(vlan_id)
        if str_vlan_id not in cls.vlan_db["vlans"]:
            raise KeyError(f"VLAN with ID {vlan_id} does not exist.")
        
        existing_ports = cls.vlan_db["vlans"][str_vlan_id]["ports"]
        updated_ports = existing_ports + ports_to_add
        cls.vlan_db["vlans"][str_vlan_id]["ports"] = updated_ports

    @classmethod
    def delete_port_from_vlan(cls, vlan_id: int, port_to_delete: int):
        """
        Delete a port from an existing VLAN.

        Args:
            vlan_id (int): The VLAN ID from which the port will be deleted.
            port_to_delete (int): The port number to be removed from the VLAN.

        Raises:
            KeyError: If the specified VLAN ID does not exist in the database.
        """
        str_vlan_id = str(vlan_id)
        if str_vlan_id not in cls.vlan_db["vlans"]:
            raise KeyError(f"VLAN with ID {vlan_id} does not exist.")
        
        existing_ports = cls.vlan_db["vlans"][str_vlan_id]["ports"]
        if port_to_delete in existing_ports:
            existing_ports.remove(port_to_delete)

    @classmethod
    def generate_router_config(cls) -> str:
        """
        Generate a Cisco router configuration based on VLAN information.

        Returns:
            str: Cisco router configuration.
        """
        config_lines = []

        # Define VLANs in the configuration
        for vlan_id, vlan_data in cls.vlan_db["vlans"].items():
            config_lines.append(f'vlan {vlan_id}')
            
            # Check if the VLAN name is not None before adding it to the configuration
            if vlan_data["name"] is not None:
                config_lines.append(f' name {vlan_data["name"]}')
            
            # Check if the VLAN description is not None before adding it to the configuration
            if vlan_data["description"] is not None:
                config_lines.append(f' description {vlan_data["description"]}')
            
            config_lines.append('!')

        # Generate interface assignments
        for vlan_id, vlan_data in cls.vlan_db["vlans"].items():
            for port in vlan_data["ports"]:
                config_lines.append(f'interface FastEthernet0/{port}')
                config_lines.append(f' switchport access vlan {vlan_id}')
                config_lines.append('!')

        return "\n".join(config_lines)

    @classmethod
    def get_vlan(cls, vlan_id: int) -> Optional[Dict[str, any]]:
        """
        Get VLAN information by VLAN ID.

        Args:
            vlan_id (int): The VLAN ID.

        Returns:
            dict: VLAN information (name, description, ports), or None if VLAN not found.
        """
        return cls.vlan_db["vlans"].get(str(vlan_id))

    @classmethod
    def list_vlans(cls) -> List[int]:
        """
        List all VLAN IDs in the database.

        Returns:
            list: List of VLAN IDs.
        """
        return [int(vlan_id) for vlan_id in cls.vlan_db["vlans"].keys()]

    @classmethod
    def to_json(cls) -> Dict[str, Dict[str, any]]:
        """
        Serialize the VLAN database to JSON.

        Returns:
            dict: JSON representation of the database.
        """
        return cls.vlan_db

    @classmethod
    def from_json(cls, json_data: Dict[str, Dict[str, any]]):
        """
        Populate the VLAN database from a JSON object.

        Args:
            json_data (dict): JSON representation of the database.
        """
        cls.vlan_db = json_data
