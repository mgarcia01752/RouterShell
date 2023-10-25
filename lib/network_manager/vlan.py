import logging

from tabulate import tabulate
from lib.db.sqlite_db.router_shell_db import Result 
from lib.network_manager.common.mac import MacServiceLayer
from lib.db.vlan_db import VLANDatabase
from lib.network_manager.bridge import Bridge

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_manager import InterfaceType
class Vlan(MacServiceLayer):

    VLAN_PREFIX_ID = "Vlan"
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg

    def does_vlan_id_exist_in_vlan_db(self, vlan_id:int) -> bool:
        return VLANDatabase().vlan_exists(vlan_id)
    
    def add_vlan_to_db(self, vlan_id: int, vlan_name: str = None) -> Result:
        """
        Add a VLAN to the database.

        Args:
            vlan_id (int): The unique ID of the VLAN.
            vlan_name (str, optional): The name of the VLAN. If not provided, a default name will be generated.

        Returns:
            InsertResult: An instance of the InsertResult class containing information about the operation's status and the row ID.

        Note:
        - If `vlan_name` is not provided, a default name is generated based on the `vlan_id`.
        - This method calls the `add_vlan` method of `VLANDatabase` to add the VLAN to the database and returns an InsertResult.
        """
        if not vlan_name:
            vlan_name = f'vlan{str(vlan_id)}'
        return VLANDatabase().add_vlan(vlan_id, vlan_name)

    def update_vlan_name(self, vlan_id: int, vlan_name: str) -> Result:
        """
        Update the name of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_name (str): The new name for the VLAN.

        Returns:
            InsertResult: An instance of the InsertResult class containing information about the operation's status and the row ID.

        Note:
        - This method calls the `update_vlan_name` method of `VLANDatabase` to update the VLAN's name in the database.
        """
        self.log.info(f"update_vlan_name() -> VlanID: {vlan_id} -> VlanName: {vlan_name}")
        
        return VLANDatabase().update_vlan_name_via_vlanID(vlan_id, vlan_name)

    def update_vlan_description_to_db(self, vlan_id: int, vlan_description: str) -> Result:
        """
        Update the description of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Returns:
            InsertResult: An instance of the InsertResult class containing information about the operation's status and the row ID.

        Note:
        - This method calls the `update_vlan_description_by_vlan_id` method of `VLANDatabase` to update the VLAN's description in the database.
        """
        return VLANDatabase().update_vlan_description_by_vlan_id(vlan_id, vlan_description)

    def add_vlan_if_not_exist(self, interface_name: str, vlan_id: int) -> bool:
        """
        Add a VLAN interface if it doesn't already exist.

        Args:
            ifName (str): The parent network interface name.
            vlan_id (str): The VLAN ID to add.

        Returns:
            bool: True if the VLAN interface was successfully added or already exists, False otherwise.
        """
        # Check if the VLAN interface already exists
        existing_vlans = self.run(["ip", "link", "show", "type", "vlan"])

        if f"{self.VLAN_PREFIX_ID}.{str(vlan_id)}" in existing_vlans:
            print(f"VLAN interface {interface_name}.{str(vlan_id)} already exists.")
            return STATUS_NOK
        
        # Create the VLAN interface
        result = self.run(["ip", "link", "add", "link", interface_name, "name", f"{interface_name}.{str(vlan_id)}", "type", "vlan", "id", str(vlan_id)])

        if result.exit_code:
            self.log.error(f"Unable to create Vlan: {str(vlan_id)}")
            return STATUS_NOK
        return STATUS_OK

    def get_vlan_config(self):
        return VLANDatabase().generate_router_config()

    def add_bridge_to_vlan(self, bridge_name:str, vlan_id:int) -> str:
        
        if Bridge().does_bridge_exist_os(bridge_name):
            self.log.debug(f"Bridge does not exists: {bridge_name}")
            return STATUS_NOK
        
        if self.add_interface_to_vlan(bridge_name, vlan_id):
            self.log.debug(f"Unable to add bridge: {bridge_name} to vlan: {vlan_id}")
            return STATUS_NOK

    def add_interface_to_vlan(self, interface_name: str, vlan_id: int, interface_type:InterfaceType) -> bool:
        """
        Add an interface to a VLAN.

        Args:
            interface_name (str): The name of the network interface.
            vlan_id (int): The VLAN ID to assign to the VLAN.
            interface_type (InterfaceType):

        Returns:
            str: A status indicating the result of the operation:
                - 'STATUS_OK' if the interface was successfully added to the VLAN.
                - 'STATUS_NOK' if the operation failed due to invalid parameters or other issues.
        """
        if vlan_id <= 0 or vlan_id > 4096:
            self.log.debug(f"add_interface_to_vlan() Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_in_vlan_db(vlan_id):
            self.log.debug(f"add_interface_to_vlan() Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        vlan_name = VLANDatabase.get_vlan_name(vlan_id)

        # Execute the command to add the interface to the VLAN
        result = self.run(['ip', 'link', 'add', 'link', interface_name, 'name', vlan_name , 'type', 'vlan', 'id', str(vlan_id)], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Unable to add VLAN {vlan_name} to interface: {interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def del_interface_to_vlan(self, vlan_id: int) -> bool:
        """
        Delete an interface from a VLAN.

        Args:
            ifName (str): The name of the network interface.
            vlan_id (int): The VLAN ID to assign to the VLAN.

        Returns:
            str: A status indicating the result of the operation:
                - STATUS_OK if the interface was successfully added to the VLAN.
                - STATUS_NOK if the operation failed due to invalid parameters or other issues.
        """
        if vlan_id <= 0 or vlan_id > 4096:
            self.log.debug(f"del_interface_to_vlan() Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_in_vlan_db(vlan_id):
            self.log.debug(f"del_interface_to_vlan() Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        vlan_name = VLANDatabase().get_vlan_name(vlan_id)
        
        # ip link delete dev vlan1000@br10
        result = self.run(['ip', 'link', 'delete', 'dev', vlan_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Unable to del VLAN {vlan_name}")
            self.log.error(f"Error: {result.stderr}")
            return STATUS_NOK

        return STATUS_OK

    def get_vlan_info(self, arg=None):

        # Run the 'ip -o link show type vlan' command and capture the output
        output = self.run(['ip', '-o', 'link', 'show', 'type', 'vlan'])

        # Split the output into lines and process each line
        lines = output.stdout.strip().split('\n')
        data = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 7:
                vlan_info = parts[0]  # Full VLAN info including VLAN ID
                vlan_id = parts[1].split('@')[0]  # Extract VLAN ID
                interface = parts[1].split('@')[1]
                mac_address = parts[16]
                state = parts[8]
                data.append([vlan_id, mac_address, interface, state])

        # Display the VLAN information as a table
        headers = ['VLAN ID', 'MAC Address', 'Interface', 'State']
        print(tabulate(data, headers, tablefmt='plain'))
    
    def get_vlan_db(self):
        return VLANDatabase().show_vlans()