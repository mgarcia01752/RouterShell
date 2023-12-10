import logging

from tabulate import tabulate
from lib.db.sqlite_db.router_shell_db import Result 
from lib.network_manager.common.mac import MacServiceLayer
from lib.db.vlan_db import VLANDatabase
from lib.network_manager.bridge import Bridge

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_manager import InterfaceType, NetworkManager
class Vlan(NetworkManager):

    VLAN_PREFIX_ID = "Vlan"
    VLAN_MAX_ID = 4096
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().VLAN)
        self.arg = arg

    def does_vlan_id_exist_in_vlan_db(self, vlan_id:int) -> bool:
        return VLANDatabase().vlan_exists(vlan_id)
    
    def check_or_add_vlan_to_db(self, vlan_id: int, vlan_name: str = None) -> Result:
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
        self.log.debug(f"update_vlan_name() -> VlanID: {vlan_id} -> VlanName: {vlan_name}")
        
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

    def add_bridge_to_vlan(self, bridge_name: str, vlan_id: int) -> str:
        """
        Add a bridge to a VLAN.

        Args:
            bridge_name (str): The name of the bridge to be added to the VLAN.
            vlan_id (int): The VLAN ID to which the bridge should be added.

        Returns:
            str: A status code indicating the outcome of the operation.
                - If the bridge does not exist, returns STATUS_NOK.
                - If the interface cannot be added to the VLAN, returns STATUS_NOK.
                - If the operation is successful, returns STATUS_OK.

        Example:
        You can use the add_bridge_to_vlan method to add a bridge to a VLAN.
        For example:
        ```
        status = your_instance.add_bridge_to_vlan('br0', 10)
        
        if status == STATUS_NOK:
            print(f"Failed to add bridge to VLAN: {status}")
        else:
            print(f"Bridge successfully added to VLAN: {status}")
        ```
        """
        if Bridge().does_bridge_exist_os(bridge_name):
            self.log.debug(f"Bridge does not exist: {bridge_name}")
            return STATUS_NOK
        
        if self.add_interface_to_vlan(bridge_name, vlan_id):
            self.log.debug(f"Unable to add bridge: {bridge_name} to VLAN: {vlan_id}")
            return STATUS_NOK
        
        return STATUS_OK

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
        if vlan_id <= 0 or vlan_id > self.VLAN_MAX_ID:
            self.log.debug(f"add_interface_to_vlan({interface_type.name}) Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_in_vlan_db(vlan_id):
            self.log.debug(f"add_interface_to_vlan({interface_type.name}) Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        db_result = VLANDatabase().get_vlan_name(vlan_id)

        if db_result.status:
            self.log.error(f"Unable to obtain vlan-name from vlan-id: {vlan_id}")
            return STATUS_NOK

        vlan_name = db_result.result.get('VlanName')

        if vlan_name is None:
            self.log.error(f"VLAN name not found for vlan-id: {vlan_id}")
            return STATUS_NOK

        result = self.run(['ip', 'link', 'add', 'link', interface_name, 'name', vlan_name , 'type', 'vlan', 'id', str(vlan_id)], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Unable to add VLAN {vlan_name} to interface: {interface_name} via OS")
            return STATUS_NOK
        
        return VLANDatabase().add_vlan_to_interface_type(vlan_id, interface_name, interface_type)

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
        if vlan_id <= 0 or vlan_id > self.VLAN_MAX_ID:
            self.log.debug(f"del_interface_to_vlan() Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_in_vlan_db(vlan_id):
            self.log.debug(f"del_interface_to_vlan() Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        db_result = VLANDatabase().get_vlan_name(vlan_id)

        if not db_result.status:
            self.log.error(f"Unable to obtain vlan-name from vlan-id: {vlan_id}")
            return STATUS_NOK

        vlan_name = db_result.result.get('VlanName')

        if vlan_name is None:
            self.log.error(f"VLAN name not found for vlan-id: {vlan_id}")
            return STATUS_NOK
        
        result = self.run(['ip', 'link', 'delete', 'dev', vlan_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Unable to del VLAN {vlan_name}")
            self.log.error(f"Error: {result.stderr}")
            return STATUS_NOK

        return STATUS_OK

    def get_vlan_info(self, arg=None):
        """
        Retrieve information about VLANs from the system.

        Args:
            arg (str, optional): Additional argument to customize the VLAN information retrieval.
                (Note: The current implementation doesn't use this argument.)

        Returns:
            None: The method prints the VLAN information as a table and doesn't return a value.

        Example:
        You can use the get_vlan_info method to display information about VLANs on the system.
        For example:
        ```
        your_instance.get_vlan_info()
        ```
        This will print the VLAN information as a table with columns for VLAN ID, MAC Address, Interface, and State.
        """
        output = self.run(['ip', '-o', 'link', 'show', 'type', 'vlan'])

        lines = output.stdout.strip().split('\n')
        data = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 7:
                vlan_info = parts[0]                # Full VLAN info including VLAN ID
                vlan_id = parts[1].split('@')[0]    # Extract VLAN ID
                interface = parts[1].split('@')[1]
                mac_address = parts[16]
                state = parts[8]
                data.append([vlan_id, mac_address, interface, state])

        # Display the VLAN information as a table
        headers = ['VLAN ID', 'MAC Address', 'Interface', 'State']
        print(tabulate(data, headers, tablefmt='plain'))

    def get_vlan_db(self):
        return VLANDatabase().show_vlans()