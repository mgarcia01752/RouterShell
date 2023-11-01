import sqlite3
import logging
import os
from typing import List

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_manager import InterfaceType

from lib.cli.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
class Result:
    """
    Represents the result of an operation in the database.

    This class is designed to encapsulate the outcome of various database operations, providing information
    about the status, associated row ID, and an optional result message.

    Attributes:
        status (bool): A boolean indicating the operation's success: STATUS_OK (0) for success, STATUS_NOK (1) for failure.
        row_id (int, optional): The row ID associated with the database operation.
        reason (str, optional): An optional result message that provides additional information about the operation.
        result (str, optional): SQL query result

    Example:
    You can use the Result class to handle the outcome of database operations, such as insertions, updates, or deletions.
    For example, after inserting a new record into the database, you can create a Result object to represent the outcome.

    Usage:
    # STATUS_NOK 
    result = Result(status=STATUS_NOK, row_id=0, result="Record inserted unsuccessfully")
    if result.status:
        print(f"{result.reason}}. Row ID: {result.row_id}")
        
    # True
    result = Result(status=True, row_id=12, result="Record inserted successfully")
    if result.status:
        print(f"{result.reason}}. Row ID: {result.row_id}")

    Note:
    - 'status' attribute SHOULD be set to STATUS_OK (0) for successful operations and STATUS_NOK (1) for failed ones OR can be any boolean, refer to method documentation.
    - 'row_id' represents the unique identifier of the affected row, any integer > 0 for STATUS_OK or 0 for STATUS_NOK
    - 'reason' provides additional information about the operation, which is particularly useful for error messages.
    """
    def __init__(self, status: bool, row_id: int=None, reason: str=None, result=None):
        self.status = status
        self.row_id = row_id
        self.reason = reason
        self.result = result
    
    def __str__(self):
        return f"Status: {self.status}, Row ID: {self.row_id}, Reason: {self.reason}, Result: {self.result}"

class RouterShellDB:
    connection = None
    
    ROUTER_SHELL_DB = 'routershell.db'
    ROUTER_SHELL_SQL_STARTUP = '../db_schema.sql'
    ROW_ID_NOT_FOUND = 0
    FK_NOT_FOUND = -1

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_SHELL_DB)
        self.debug = CGS().DEBUG_ROUTER_SHELL_DB
                
        self.log.debug(f"__init__() - DB Connection Status -> {self.connection}")
        self.db_file_path = os.path.join(os.path.dirname(__file__), self.ROUTER_SHELL_DB)
        self.sql_file_path = os.path.join(os.path.dirname(__file__), self.ROUTER_SHELL_SQL_STARTUP)
        
        if not self.connection:
            self.log.debug(f"Connecting to DB {self.ROUTER_SHELL_DB}")
            self.create_database()
        else:
            self.log.debug(f"Already Connected to DB {self.ROUTER_SHELL_DB}")

    def create_database(self):
        """
        Create an SQLite database file and populate it with tables and data from an SQL file.
        """
        
        self.log.debug(f"create_database()")
        
        try:
            self.connection = sqlite3.connect(self.db_file_path, check_same_thread=True)
            cursor = self.connection.cursor()

            with open(self.sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()

            cursor.executescript(sql_script)

            # Commit the changes
            self.connection.commit()

            self.log.debug("SQLite database created successfully.")

        except sqlite3.Error as e:
            print("Error:", e)

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()

    '''
                        BRIDGE DATABASE
    '''

    def bridge_exist_db(self, bridge_name) -> Result:
        """
        Check if a bridge with the given name exists in the 'Bridges' table.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            Result: An instance of Result with status True if the bridge exists, False otherwise.
        """
        self.log.debug(f"bridge_exist_db() -> Bridge: {bridge_name}")

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ROWID FROM Bridges WHERE BridgeName = ?", (bridge_name,))
            row_id = cursor.fetchone()
            if row_id:
                return Result(True, row_id[0], None)
            else:
                return Result(False, self.ROW_ID_NOT_FOUND, f"Bridge: {bridge_name} not found")

        except sqlite3.Error as e:
            return Result(False, self.ROW_ID_NOT_FOUND, f"Error while checking for bridge: {bridge_name}")

    def get_bridge_id(self, bridge_name: str) -> int:
        """
        Retrieve the ID of a bridge by its name.

        Args:
            bridge_name (str): The name of the bridge.

        Returns:
            int: The ID of the bridge if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Bridges WHERE BridgeName = ?", (bridge_name))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("get_bridge_id() -> Error retrieving 'Bridges' ID: %s", e)
        return None

    def insert_bridge(self, bridge_name: str, bridge_protocol: str = None, stp_status: bool = False, bridge_group_fk: int = ROW_ID_NOT_FOUND, shutdown:bool = True) -> Result:
        """
        Insert a new bridge configuration into the 'Bridges' table.

        Args:
            bridge_name (str): The name of the bridge to insert.
            bridge_protocol (str, optional): The protocol used by the bridge (default: None).
            stp_status (bool, optional): The Spanning Tree Protocol (STP) status (default: False).
            bridge_group_fk (int, optional): The foreign key reference to the associated bridge group (default: ROW_ID_NOT_FOUND).

        Returns:
            Result: A Result object with the status of the insertion, the row ID, and a result message.
        """
        try:

            # Construct the SQL query with placeholders
            sql = "INSERT INTO Bridges (BridgeGroups_FK, BridgeName, Protocol, StpStatus, shutdownStatus) VALUES (?, ?, ?, ?, ?)"
            data = (bridge_group_fk, bridge_name, bridge_protocol, stp_status, shutdown)

            # Insert data into the database
            cursor = self.connection.cursor()
            cursor.execute(sql, data)
            self.connection.commit()
            
            # Get the last inserted row ID
            row_id = cursor.lastrowid

            return Result(STATUS_OK, row_id, "Bridge added successfully")

        except ValueError as e:
            self.log.error(f"Invalid input parameters: {e}")
            return Result(STATUS_NOK, -1, "Invalid input parameters")
        
        except sqlite3.Error as e:
            error_message = f"Error inserting data into 'Bridges': {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, -1, error_message)

    def delete_bridge_entry(self, bridge_name) -> bool:
        try:
            cursor = self.connection.cursor()

            # Get the associated Bridge ID
            cursor.execute("SELECT ID FROM Bridges WHERE BridgeName = ?", (bridge_name,))
            bridge_id = cursor.fetchone()
            
            if not bridge_id:
                self.log.error(f"Bridge entry not found for BridgeName: {bridge_name}")
                return STATUS_NOK  # Bridge entry not found

            bridge_id = bridge_id[0]  # Get the Bridge ID from the result

            # Delete records in the associated table VlanInterfaces
            cursor.execute("DELETE FROM VlanInterfaces WHERE Bridge_FK = ?", (bridge_id,))

            # Delete the bridge entry
            cursor.execute("DELETE FROM Bridges WHERE ID = ?", (bridge_id,))

            # Commit the changes
            self.connection.commit()

            return STATUS_OK

        except sqlite3.Error as e:
            self.log.error("Error deleting bridge entry: %s", e)
            return STATUS_NOK

    '''
                        VLAN DATABASE
    '''
    
    def vlan_id_exists(self, vlan_id: int) -> bool:
        """
        Check if a VLAN with the given ID exists in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to check.

        Returns:
            bool: True if the VLAN with the given ID exists, False otherwise.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Vlans WHERE ID = ?", (vlan_id,))
            result = cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            self.log.error("Error checking VLAN existence: %s", e)
            return False

    def insert_vlan(self, vlanid: int, vlan_name: str, vlan_interfaces_fk: int = ROW_ID_NOT_FOUND) -> Result:
        """
        Insert data into the 'Vlans' table.

        Args:
            vlanid (int): The unique ID of the VLAN.
            vlan_name (str): The name of the VLAN.
            vlan_interfaces_fk (int, optional): The foreign key referencing VLAN interfaces.

        Returns:
            Result: A Result object with the status and row ID of the inserted VLAN.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        self.log.debug(f"insert_vlan() -> vlanid: {vlanid}, vlan-if-fkey: {vlan_interfaces_fk}, vlan-name: {vlan_name}")

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Vlans (VlanID, VlanInterfaces_FK, VlanName) VALUES (?, ?, ?)",
                (vlanid, vlan_interfaces_fk, vlan_name)
            )

            self.connection.commit()
            self.log.debug("Data inserted into the 'Vlans' table successfully.")
            return Result(status=STATUS_OK, row_id=cursor.lastrowid)
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Vlans': %s", e)
            return Result(status=STATUS_NOK, row_id=0, reason=str(e))

    def update_vlan_name_by_vlan_id(self, vlan_id: int, vlan_name: str) -> bool:
        """
        Update the Vlan-Name of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_name (str): The new VLAN name for the VLAN.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK if it fails.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Vlans SET VlanName = ? WHERE VlanID = ?",
                (vlan_name, vlan_id)
            )
            self.connection.commit()
            self.log.debug(f"VLAN Name -> {vlan_name} of VlanID -> {vlan_id} updated successfully.")
            return STATUS_OK
        except sqlite3.Error as e:
            self.log.error("Error updating VLAN name: %s", e)
            return STATUS_NOK

    def update_vlan_description_by_vlan_id(self, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK if it fails.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Vlans SET VlanDescription = ? WHERE ID = ?",
                (vlan_description, vlan_id)
            )
            self.connection.commit()
            self.log.debug(f"Description of VLAN {vlan_id} updated successfully.")
            return STATUS_OK
        except sqlite3.Error as e:
            self.log.error("Error updating VLAN description: %s", e)
            return STATUS_NOK

    def insert_vlan_interface(self, id: int, vlan_name: str, interface_fk: int, bridge_fk: int):
        """
        Insert data into the 'VlanInterfaces' table.

        Args:
            id (int): The unique ID of the VLAN interface.
            vlan_name (str): The name of the VLAN.
            interface_fk (int): The foreign key referencing an interface.
            bridge_fk (int): The foreign key referencing a bridge.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO VlanInterfaces (ID, VlanName, Interface_FK, Bridge_FK) VALUES (?, ?, ?, ?)",
                (id, vlan_name, interface_fk, bridge_fk)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'VlanInterfaces' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'VlanInterfaces': %s", e)

    def show_vlans(self):
        try:


            # SQL query to retrieve VLAN information
            query = """
                SELECT
                    Vlans.ID AS VLAN_ID,
                    Vlans.VlanName AS VLAN_NAME,
                    Vlans.VlanDescription AS VLAN_DESCRIPTION,
                    VlanInterfaces.ID AS INTERFACE_ID,
                    VlanInterfaces.VlanName AS INTERFACE_VLAN_NAME,
                    VlanInterfaces.Interface_FK AS INTERFACE_ID,
                    VlanInterfaces.Bridge_FK AS BRIDGE_ID
                FROM
                    Vlans
                LEFT JOIN
                    VlanInterfaces
                ON
                    Vlans.VlanInterfaces_FK = VlanInterfaces.ID;
            """
            cursor = self.connection.cursor()
            cursor.execute(query)
            vlan_data = cursor.fetchall()

            return vlan_data

        except sqlite3.Error as e:
            print("Error:", e)
            return []

    def get_vlan_interfaces_id(self, vlan_name: str) -> int:
        """
        Retrieve the ID of VLAN interfaces by the VLAN name.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            int: The ID of the VLAN interfaces if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM VlanInterfaces WHERE VlanName = ?", (vlan_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'VlanInterfaces' ID: %s", e)
        return None

    '''
                        NAT DATABASE
    '''

    def global_nat_pool_name_exists(self, pool_name: str) -> Result:
        """
        Check if a NAT pool with the given name exists in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to check for existence.

        Returns:
            Result: A Result object with the status and a boolean value indicating if the NAT pool exists.
                    `status`: True is successful, False otherwise
                    `row_id`: Row-ID of the found NAT Pool, Row-ID of 0 is Not Found

        This method queries the NAT database to determine whether a NAT pool with the provided name exists.
        If any matching pool is found, it returns a Result with STATUS_OK and True; otherwise, it returns
        a Result with STATUS_OK and False.

        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Nats WHERE NatPoolName = ?", (pool_name,))
            result = cursor.fetchone()

            if result and result[0] > 0:
                self.log.debug(f"global_nat_pool_name_exists({pool_name}) Exists")
                return Result(True, row_id=result[0])
            else:
                self.log.debug(f"global_nat_pool_name_exists({pool_name}) NOT Exists")
                return Result(False, row_id=0)

        except sqlite3.Error as e:
            error_message = f"Error checking NAT pool existence: {e}"
            return Result(False, row_id=0, reason=error_message)

    def insert_global_nat_pool(self, nat_pool_name: str) -> Result:
        """
        Insert a new global NAT configuration into the 'Nats' table.

        Args:
            nat_pool_name (str): The name of the NAT pool.

        Returns:
            Result: A Result object with the status of the insertion and the row ID.
                    - 'status' STATUS_OK if successful, STATUS_NOK otherwise
        """
        self.log.debug(f"insert_global_nat_pool({nat_pool_name})")
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Nats (NatPoolName) VALUES (?)", (nat_pool_name,))
            self.connection.commit()
            
            row_id = cursor.lastrowid
            self.log.debug(f"Inserted global NAT pool '{nat_pool_name}' with row ID: {row_id}")
            
            return Result(STATUS_OK, row_id=row_id)
        except sqlite3.Error as e:
            error_message = f"Error inserting global NAT: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def delete_global_nat_pool_name(self, nat_pool_name: str) -> Result:
        """
        Delete a global NAT configuration from the 'Nats' table by NAT pool name.

        Args:
            nat_pool_name (str): The name of the NAT pool to be deleted.

        Returns:
            Result: A Result object with the status of the deletion and additional information.
                    Result.status = STATUS_OK if successful, STATUS_NOK otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Nats WHERE NatPoolName = ?", 
                           (nat_pool_name,))
            self.connection.commit()

            if cursor.rowcount > 0:
                return Result(STATUS_OK, reason="Global NAT configuration deleted successfully")
            else:
                return Result(STATUS_NOK, reason="No matching NAT pool found for deletion")

        except sqlite3.Error as e:
            error_message = f"Error deleting global NAT configuration: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def update_nat_interface_direction(self, nat_pool_name: str, interface_name: str, direction: str) -> Result:
        """
        Update the association between a global NAT pool and an inside interface in the 'NatDirections' table.

        Args:
            nat_pool_name (str): The name of the global NAT pool.
            interface_name (str): The name of the inside interface to associate with the NAT pool.
            direction (str): The inside/outside direction interface to associate with the NAT pool.
        Returns:
            Result: A Result object with the status of the update and the row_id of the inserted entry.

        This method updates the association between a global NAT pool and an inside interface in the 'NatDirections' table
        by inserting a new entry with the specified NAT pool, inside interface, and direction. The 'Direction' is set to 'inside' by default.

        Args:
        - nat_pool_name (str): The name of the global NAT pool.
        - interface_name (str): The name of the inside interface to associate with the NAT pool.

        Returns:
        - Result: An object that encapsulates the result of the update operation, including:
            - The status (STATUS_OK for success, STATUS_NOK for failure).
            - The 'row_id' of the newly inserted entry in the 'NatDirections' table.
        """
        try:
            nat_pool_result = self.get_global_nat_row_id(nat_pool_name)

            if not nat_pool_result.status:
                return nat_pool_result

            nat_pool_id = nat_pool_result.row_id

            interface_result = self.interface_exists(interface_name)

            if not interface_result.status:
                return interface_result

            interface_id = interface_result.row_id

            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO NatDirections (NAT_FK, INTERFACE_FK, Direction) VALUES (?, ?, ?)",
                        (nat_pool_id, interface_id, direction))

            # Get the row_id of the newly inserted entry
            row_id = cursor.lastrowid

            self.connection.commit()

            return Result(STATUS_OK, row_id=row_id)

        except sqlite3.Error as e:
            error_message = f"Error updating global NAT interface FK: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def get_global_nat_row_id(self, nat_pool_name: str) -> Result:
        """
        Retrieve the row ID of a global NAT configuration in the 'Nats' table based on its name.

        Args:
            nat_pool_name (str): The name of the NAT pool.

        Returns:
            Result: A Result object with the status and the row ID of the NAT pool if found.
            
            status: STATUS_OK successful, STATUS_NOK otherwise
            row_id: STATUS_OK = row-id, STATUS_NOK = row-id=0
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Nats WHERE NatPoolName = ?", (nat_pool_name,))
            row = cursor.fetchone()

            if row is not None:
                row_id = row[0]
                return Result(STATUS_OK, row_id=row_id)
            else:
                error_message = f"Global NAT pool '{nat_pool_name}' not found."
                self.log.error(error_message)
                return Result(STATUS_NOK, reason=error_message)

        except sqlite3.Error as e:
            error_message = f"Error retrieving global NAT row ID: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def insert_interface_nat_direction(self, interface_name: str, nat_pool_name: str, direction: str) -> Result:
        """
        Insert a new NAT direction configuration into the 'NatDirections' table.

        Args:
            interface_name (str): The name of the interface for the NAT direction.
            nat_pool_name (str): The name of the NAT pool associated with the direction.
            direction (str): The direction (e.g., 'inside' or 'outside').

        Returns:
            Result: A Result object with the status of the insertion.
        """
        try:
            self.log.debug(f"insert_interface_nat_direction(Parameters: {interface_name} -> {nat_pool_name} -> {direction})")
            
            nat_pool_result = self.get_global_nat_row_id(nat_pool_name)

            if nat_pool_result.status:
                nat_pool_error = f"Unable to insert Interface-Nap-Pool, nat-pool-name: ({nat_pool_name}) does not exists"
                self.log.error(f"{nat_pool_error}")
                return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=nat_pool_error)

            nat_pool_id = nat_pool_result.row_id

            interface_result = self.interface_exists(interface_name)

            if not interface_result.status:
                if_pool_error = f"Unable to insert Interface-Nap-Pool, interface: ({interface_name}) does not exists"
                self.log.error(f"{if_pool_error}")
                return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=if_pool_error)

            interface_id = interface_result.row_id

            self.log.debug(f"insert_interface_nat_direction(if-id: {interface_id} -> nat-pool-id: {nat_pool_id} -> {direction})")
            
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO NatDirections (NAT_FK, Interface_FK, Direction) VALUES (?, ?, ?)", 
                                (nat_pool_id, interface_id, direction))

            self.connection.commit()
            inserted_row_id = cursor.lastrowid

            return Result(STATUS_OK, row_id=inserted_row_id)

        except sqlite3.Error as e:
            error_message = f"Error inserting NAT direction: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def delete_interface_nat_direction(self, interface_name: str, nat_pool_name: str) -> Result:
        """
        Delete all NAT direction configurations for a specified interface and NAT pool.

        Args:
            interface_name (str): The name of the interface for which NAT directions should be deleted.
            nat_pool_name (str): The name of the NAT pool associated with the directions.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        try:
            nat_pool_result = self.get_global_nat_row_id(nat_pool_name)

            if not nat_pool_result.status:
                return nat_pool_result

            nat_pool_id = nat_pool_result.row_id

            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM NatDirections WHERE NAT_FK = ? AND INTERFACE_FK = ?", 
                                (nat_pool_id, interface_name))
            self.connection.commit()
            return Result(STATUS_OK)

        except sqlite3.Error as e:
            error_message = f"Error deleting NAT directions: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def get_global_nat_pool_names(self) -> list:
        """
        Retrieve a list of global NAT pool names from the NAT database.

        Returns:
            list: A list of NAT pool names.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT NatPoolName FROM Nats")
            pool_names = [row[0] for row in cursor.fetchall()]
            return pool_names

        except sqlite3.Error as e:
            self.log.error(f"An error occurred while retrieving global NAT pool names: {e}")
            return []

    def inside_interface_exists(self, pool_name: str, interface_name: str) -> Result:
        """
        Check if an inside interface is associated with a NAT pool configuration.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface to check.

        Returns:
            Result: A Result object with the status and a boolean value indicating if the inside interface is associated with the NAT pool.
            status: True if inside interface exist, otherwise False
        """
        
        '''avoid circular imports'''
        from lib.network_manager.nat import NATDirection
        
        try:
            if not pool_name or not interface_name:
                error_message = "Invalid input: Pool name and interface name must be provided."
                return Result(STATUS_NOK, reason=error_message)

            pool_exists_result = self.global_nat_pool_name_exists(pool_name)

            if not pool_exists_result.status:
                return pool_exists_result

            if not pool_exists_result.reason:
                return Result(False, reason=False)

            interface_exists_result = self.interface_exists(interface_name)

            if not interface_exists_result.status:
                return interface_exists_result

            if not interface_exists_result.reason:
                return Result(False, reason=False)

            nat_pool_id_result = self.get_global_nat_row_id(pool_name)
            interface_id_result = self.get_interface_id(interface_name)

            if not nat_pool_id_result.status:
                return nat_pool_id_result

            if not interface_id_result.status:
                return interface_id_result

            nat_pool_id = nat_pool_id_result.row_id
            interface_id = interface_id_result.row_id

            direction_exists = self._interface_nat_direction_exists(nat_pool_id, interface_id, NATDirection.INSIDE)

            return Result(True, reason=direction_exists)

        except Exception as e:
            error_message = f"An error occurred while checking inside interface association: {e}"
            return Result(False, reason=error_message)

    def nat_direction_interface_exists(self, pool_name: str, interface_name: str, direction:str) -> Result:
        
        try:
            if not pool_name or not interface_name:
                error_message = "Invalid input: Pool name and interface name must be provided."
                return Result(STATUS_NOK, reason=error_message)

            pool_exists_result = self.global_nat_pool_name_exists(pool_name)

            if not pool_exists_result.status:
                return pool_exists_result

            if not pool_exists_result.reason:
                return Result(False, reason=False)

            interface_exists_result = self.interface_exists(interface_name)

            if not interface_exists_result.status:
                return interface_exists_result

            if not interface_exists_result.reason:
                return Result(False, reason=False)

            nat_pool_id_result = self.get_global_nat_row_id(pool_name)
            interface_id_result = self.get_interface_id(interface_name)

            if not nat_pool_id_result.status:
                return nat_pool_id_result

            if not interface_id_result.status:
                return interface_id_result

            nat_pool_id = nat_pool_id_result.row_id
            interface_id = interface_id_result.row_id

            direction_exists = self._interface_nat_direction_exists(nat_pool_id, interface_id, direction)

            return Result(True, reason=direction_exists)

        except Exception as e:
            error_message = f"An error occurred while checking inside interface association: {e}"
            return Result(False, reason=error_message)

    def _interface_nat_direction_exists(self, nat_id: int, interface_id: int, direction: str) -> Result:
        """
        Check if a specific NAT direction exists for a given NAT pool and inside/outside interface.

        Args:
            nat_id (int): The ID of the NAT pool.
            interface_id (int): The ID of the inside/outside interface.
            direction (str): The direction to check (e.g., 'inside' or 'outside').

        Returns:
            bool: True if the specified NAT direction exists, False otherwise.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM NatDirections WHERE NAT_FK = ? AND INTERFACE_FK = ? AND Direction = ?", 
                           (nat_id, interface_id, direction))
            result = cursor.fetchone()
            
            return result[0] > 0
                    
        except sqlite3.Error as e:
            self.log.error(f"An error occurred while checking NAT direction existence: {e}")
            return False

    def get_nat_interface_direction(self, interface_name: str, nat_pool_name: str, direction: str) -> Result:
        """
        Check if the specified interface is associated with the given NAT pool and direction.

        Args:
            interface_name (str): The name of the interface to check.
            nat_pool_name (str): The name of the NAT pool to check.
            direction (str): The direction to check (inside or outside).

        Returns:
            Result: A Result object with the following fields:
                - status (bool): True if the interface is found in the specified NAT pool and direction, False otherwise.
                - row_id (int): The row ID of the found entry, or 0 if not found.

        Raises:
            sqlite3.Error: If there is an error with the database query.

        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Nats WHERE NatPoolName = ?", (nat_pool_name,))
            nat_pool_result = cursor.fetchone()

            if nat_pool_result is None:
                return Result(status=False, row_id=0)  # NAT pool not found

            nat_pool_id = nat_pool_result[0]
            
            cursor.execute("SELECT ID FROM Interfaces WHERE InterfaceName = ?", (interface_name,))
            interface_result = cursor.fetchone()
            interface_id = interface_result[0]
            
            self.log.debug(f"get_nat_interface_direction_list() - NAT-POOL-ID: {nat_pool_id} - InterfaceID: ({interface_result[0]})")

            if interface_result is None:
                return Result(status=False, row_id=0)  # Interface not found

            cursor.execute("SELECT ID FROM NatDirections WHERE NAT_FK = ? AND Interface_FK = ? AND Direction = ?",
                           (nat_pool_id, interface_id, direction))
            nat_direction_result = cursor.fetchone()

            if nat_direction_result is not None:
                self.log.debug(f"get_nat_interface_direction() - interface: {interface_name} -> nat-pool: {nat_pool_name} - direction: {direction} -> Result: Found")                
                return Result(status=True, row_id=nat_direction_result[0])
            else:
                msg = f"interface: {interface_name} -> nat-pool: {nat_pool_name} - direction: {direction} -> Result: Not-Found"
                self.log.debug(f"get_nat_interface_direction() - {msg}")
                return Result(status=False, row_id=0, reason=msg)

        except sqlite3.Error as e:
            error_message = f"Error checking NAT interface direction: {e}"
            self.log.critical(error_message)
            return Result(status=False, row_id=0, reason=error_message)

    def get_nat_interface_direction_list(self, nat_pool_name: str, direction: str) -> List[Result]:
        try:
            cursor = self.connection.cursor()
            results = []

            cursor.execute("""
                SELECT ND.Interface_FK, I.InterfaceName
                FROM NatDirections AS ND
                JOIN Interfaces AS I ON ND.Interface_FK = I.ID
                JOIN Nats AS N ON ND.NAT_FK = N.ID
                WHERE N.NatPoolName = ? AND ND.Direction = ?
            """, (nat_pool_name, direction))

            rows = cursor.fetchall()
            for row in rows:
                interface_id, interface_name = row
                result = Result(status=True, row_id=interface_id, result=interface_name)
                results.append(result)

            return results
        except sqlite3.Error as e:
            # Handle the database error, possibly log it or raise a custom exception
            raise e

    '''
                        DHCP DATABASE
    '''

    def get_dhcp_pool_name_id(self, dhcp_poolname: str) -> int:
        """
        Retrieve the ID of a DHCP configuration by its pool name.

        Args:
            dhcp_poolname (str): The name of the DHCP pool.

        Returns:
            int: The ID of the DHCP configuration if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM DHCP WHERE DhcpPoolname = ?", (dhcp_poolname,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'DHCP' ID: %s", e)
        return None
    
    def insert_dhcp_server_pool_name(self, dhcp_pool_name:str) -> Result:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO DHCPools (DhcpPoolname) VALUES (?)",
                (dhcp_pool_name,)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'DHCPools' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'DHCP': %s", e)        
    
    def _insert_dhcp_server_pool_name(self, id: int, interface_fk: int, dhcp_poolname: str):
        """
        Insert data into the 'DHCP' table.

        Args:
            id (int): The unique ID of the DHCP configuration.
            interface_fk (int): The foreign key referencing an interface.
            dhcp_poolname (str): The name of the DHCP pool.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO DHCP (id, Interface_FK, DhcpPoolname) VALUES (?, ?, ?)",
                (id, interface_fk, dhcp_poolname)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'DHCP' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'DHCP': %s", e)

    def get_global_options(self, dhcp_fk: int) -> list:
        """
        Retrieve the global options associated with a DHCP configuration by its foreign key.

        Args:
            dhcp_fk (int): The foreign key referencing DHCP configuration.

        Returns:
            list: A list of global options associated with the DHCP configuration if found, or an empty list if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        options = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DhcpOptions, DhcpValue FROM OptionsGlobal WHERE DHCP_FK = ?", (dhcp_fk,))
            rows = cursor.fetchall()
            if rows:
                options = [{"DhcpOptions": row[0], "DhcpValue": row[1]} for row in rows]
        except sqlite3.Error as e:
            self.log.error("Error retrieving global options: %s", e)
        return options

    '''
                    DHCP-SUBNET DATABASE
    '''
    def get_subnet_id(self, ip_subnet: str) -> int:
        """
        Retrieve the ID of a subnet by its IP subnet.

        Args:
            ip_subnet (str): The IP subnet.

        Returns:
            int: The ID of the subnet if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM Subnet WHERE IpSubnet = ?", (ip_subnet,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Subnet' ID: %s", e)
        return None

    def insert_subnet(self, id: int, dhcp_fk: int, ip_subnet: str):
        """
        Insert data into the 'Subnet' table.

        Args:
            id (int): The unique ID of the subnet.
            dhcp_fk (int): The foreign key referencing DHCP configuration.
            ip_subnet (str): The IP subnet.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Subnet (id, DHCP_FK, IpSubnet) VALUES (?, ?, ?)",
                (id, dhcp_fk, ip_subnet)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'Subnet' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Subnet': %s", e)

    '''
                    DHCP-POOLS DATABASE
    '''
    
    def insert_pools(self, id: int, subnet_fk: int, ip_address_start: str, ip_address_end: str, ip_subnet: str):
        """
        Insert data into the 'Pools' table.

        Args:
            id (int): The unique ID of the pool.
            subnet_fk (int): The foreign key referencing a subnet.
            ip_address_start (str): The start IP address of the pool.
            ip_address_end (str): The end IP address of the pool.
            ip_subnet (str): The IP subnet of the pool.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Pools (id, Subnet_FK, IpAddressStart, IpAddressEnd, IpSubnet) VALUES (?, ?, ?, ?, ?)",
                (id, subnet_fk, ip_address_start, ip_address_end, ip_subnet)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'Pools' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Pools': %s", e)

    def insert_options_pools(self, id: int, pools_fk: int, dhcp_options: str, dhcp_value: str):
        """
        Insert data into the 'OptionsPools' table.

        Args:
            id (int): The unique ID of the pool options.
            pools_fk (int): The foreign key referencing a pool.
            dhcp_options (str): The DHCP options.
            dhcp_value (str): The value of the DHCP options.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO OptionsPools (id, Pools_FK, DhcpOptions, DhcpValue) VALUES (?, ?, ?, ?)",
                (id, pools_fk, dhcp_options, dhcp_value)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'OptionsPools' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'OptionsPools': %s", e)

    def insert_options_global(self, id: int, dhcp_fk: int, dhcp_options: str, dhcp_value: str):
        """
        Insert data into the 'OptionsGlobal' table.

        Args:
            id (int): The unique ID of the global options.
            dhcp_fk (int): The foreign key referencing DHCP configuration.
            dhcp_options (str): The DHCP options.
            dhcp_value (str): The value of the DHCP options.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO OptionsGlobal (id, DHCP_FK, DhcpOptions, DhcpValue) VALUES (?, ?, ?, ?)",
                (id, dhcp_fk, dhcp_options, dhcp_value)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'OptionsGlobal' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'OptionsGlobal': %s", e)

    def get_pools_id(self, ip_address_start: str, ip_address_end: str) -> int:
        """
        Retrieve the ID of a pool by its start and end IP addresses.

        Args:
            ip_address_start (str): The start IP address of the pool.
            ip_address_end (str): The end IP address of the pool.

        Returns:
            int: The ID of the pool if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM Pools WHERE IpAddressStart = ? AND IpAddressEnd = ?", (ip_address_start, ip_address_end))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Pools' ID: %s", e)
        return None

    def get_options_pools_id(self, dhcp_options: str, dhcp_value: str) -> int:
        """
        Retrieve the ID of pool options by DHCP options and value.

        Args:
            dhcp_options (str): The DHCP options.
            dhcp_value (str): The value of the DHCP options.

        Returns:
            int: The ID of the pool options if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM OptionsPools WHERE DhcpOptions = ? AND DhcpValue = ?", (dhcp_options, dhcp_value))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'OptionsPools' ID: %s", e)
        return None

    def get_options_global_id(self, dhcp_options: str, dhcp_value: str) -> int:
        """
        Retrieve the ID of global options by DHCP options and value.

        Args:
            dhcp_options (str): The DHCP options.
            dhcp_value (str): The value of the DHCP options.

        Returns:
            int: The ID of the global options if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM OptionsGlobal WHERE DhcpOptions = ? AND DhcpValue = ?", (dhcp_options, dhcp_value))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'OptionsGlobal' ID: %s", e)
        return None

    def get_pool_options(self, pools_fk: int) -> list:
        """
        Retrieve the options associated with a pool by its foreign key.

        Args:
            pools_fk (int): The foreign key referencing a pool.

        Returns:
            list: A list of options associated with the pool if found, or an empty list if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        options = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DhcpOptions, DhcpValue FROM OptionsPools WHERE Pools_FK = ?", (pools_fk,))
            rows = cursor.fetchall()
            if rows:
                options = [{"DhcpOptions": row[0], "DhcpValue": row[1]} for row in rows]
        except sqlite3.Error as e:
            self.log.error("Error retrieving pool options: %s", e)
        return options

    '''
                    DHCP-RESERVATIONS DATABASE
    '''

    def get_options_reservations(self, pool_reservations_fk: int) -> list:
        """
        Retrieve the options associated with a pool reservations entry by its foreign key.

        Args:
            pool_reservations_fk (int): The foreign key referencing a pool reservations entry.

        Returns:
            list: A list of options associated with the pool reservations entry if found, or an empty list if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        options = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DhcpOptions, DhcpValue FROM OptionsReservations WHERE PoolReservations_FK = ?", (pool_reservations_fk,))
            rows = cursor.fetchall()
            if rows:
                options = [{"DhcpOptions": row[0], "DhcpValue": row[1]} for row in rows]
        except sqlite3.Error as e:
            self.log.error("Error retrieving pool reservations options: %s", e)
        return options

    def insert_reservations(self, id: int, subnet_fk: int, mac_address: str, ip_address: str):
        """
        Insert data into the 'Reservations' table.

        Args:
            id (int): The unique ID of the reservation.
            subnet_fk (int): The foreign key referencing a subnet.
            mac_address (str): The MAC address of the reservation.
            ip_address (str): The IP address of the reservation.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Reservations (id, Subnet_FK, MacAddress, IPAddress) VALUES (?, ?, ?, ?)",
                (id, subnet_fk, mac_address, ip_address)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'Reservations' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Reservations': %s", e)

    def insert_options_reservations(self, id: int, pool_reservations_fk: int, dhcp_options: str, dhcp_value: str):
        """
        Insert data into the 'OptionsReservations' table.

        Args:
            id (int): The unique ID of the reservation options.
            pool_reservations_fk (int): The foreign key referencing a pool reservations entry.
            dhcp_options (str): The DHCP options.
            dhcp_value (str): The value of the DHCP options.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO OptionsReservations (id, PoolReservations_FK, DhcpOptions, DhcpValue) VALUES (?, ?, ?, ?)",
                (id, pool_reservations_fk, dhcp_options, dhcp_value)
            )
            self.connection.commit()
            self.log.debug("Data inserted into the 'OptionsReservations' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'OptionsReservations': %s", e)

    def get_reservations_id(self, mac_address: str, ip_address: str) -> int:
        """
        Retrieve the ID of a reservation by MAC address and IP address.

        Args:
            mac_address (str): The MAC address of the reservation.
            ip_address (str): The IP address of the reservation.

        Returns:
            int: The ID of the reservation if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM Reservations WHERE MacAddress = ? AND IPAddress = ?", (mac_address, ip_address))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Reservations' ID: %s", e)
        return None

    def get_options_reservations_id(self, dhcp_options: str, dhcp_value: str) -> int:
        """
        Retrieve the ID of reservation options by DHCP options and value.

        Args:
            dhcp_options (str): The DHCP options.
            dhcp_value (str): The value of the DHCP options.

        Returns:
            int: The ID of the reservation options if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM OptionsReservations WHERE DhcpOptions = ? AND DhcpValue = ?", (dhcp_options, dhcp_value))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'OptionsReservations' ID: %s", e)
        return None

    def get_dhcp_subnets(self, dhcp_fk: int) -> list:
        """
        Retrieve the subnets associated with a DHCP configuration by its foreign key.

        Args:
            dhcp_fk (int): The foreign key referencing DHCP configuration.

        Returns:
            list: A list of subnets associated with the DHCP configuration if found, or an empty list if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        subnets = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT IpSubnet FROM Subnet WHERE DHCP_FK = ?", (dhcp_fk,))
            rows = cursor.fetchall()
            if rows:
                subnets = [row[0] for row in rows]
        except sqlite3.Error as e:
            self.log.error("Error retrieving DHCP subnets: %s", e)
        return subnets

    def get_pool_reservations(self, subnet_fk: int) -> list:
        """
        Retrieve the pool reservations associated with a subnet by its foreign key.

        Args:
            subnet_fk (int): The foreign key referencing a subnet.

        Returns:
            list: A list of pool reservations associated with the subnet if found, or an empty list if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        reservations = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MacAddress, IPAddress FROM Reservations WHERE Subnet_FK = ?", (subnet_fk,))
            rows = cursor.fetchall()
            if rows:
                reservations = [{"MacAddress": row[0], "IPAddress": row[1]} for row in rows]
        except sqlite3.Error as e:
            self.log.error("Error retrieving pool reservations: %s", e)
        return reservations

    '''
                        DHCP-CLIENT DATABASE
    '''

    def insert_interface_dhcp_client(self, interface_name: str, dhcp_version: str) -> Result:
        """
        Insert a new DHCP client entry into the database.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (str): The DHCP version (DHCP_V4 or DHCP_V6).

        Returns:
            Result: A Result object with the status of the insertion and the row ID.
                    status = STATUS_OK for success, STATUS_NOK for failure.
        """
        result = self.interface_exists(interface_name)
        
        if not result.status:
            err = f"Unable to insert DHCP client to interface: {interface_name} does not exist"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=err)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO DHCPClient (Interface_FK, DHCPVersion) VALUES (?, ?)", (result.row_id, dhcp_version))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(STATUS_OK, row_id=row_id)
        
        except Exception as e:
            self.log.error(f"Failed to add DHCP client: {e}")
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def update_interface_dhcp_client(self, interface_name: str, dhcp_version: str) -> Result:
        """
        Update the DHCP version for an existing DHCP client entry in the database.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (str): The updated DHCP version (DHCP_V4 or DHCP_V6).

        Returns:
            Result: A Result object with the status of the update and the row ID.
                    status = STATUS_OK for success, STATUS_NOK for failure.
        """
        result = self.interface_exists(interface_name)
        
        if result.status:
            err = f"Unable to update DHCP client to interface: {interface_name} does not exist"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=err)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
            "UPDATE DHCPClient SET DHCPVersion = ? WHERE Interface_FK = ?", (dhcp_version, result.row_id))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(STATUS_OK, row_id=row_id)
        
        except Exception as e:
            self.log.error(f"Failed to update DHCP client: {e}")
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def remove_interface_dhcp_client(self, interface_name: str, dhcp_version: str) -> Result:
        """
        Remove a DHCP client entry from the database.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (str): The DHCP version to be removed (DHCP_V4 or DHCP_V6).

        Returns:
            Result: A Result object with the status of the removal and the row ID.
                    status = STATUS_OK for success, STATUS_NOK for failure.
        """
        result = self.interface_exists(interface_name)
        
        if result.status:
            err = f"Unable to remove DHCP client from interface: {interface_name} does not exist"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=err)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM DHCPClient WHERE Interface_FK = ? AND DHCPVersion = ?", (result.row_id, dhcp_version))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(STATUS_OK, row_id=row_id)
        
        except Exception as e:
            self.log.error(f"Failed to remove DHCP client: {e}")
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))


    '''
                        INTERFACE DATABASE
    '''

    def get_interface_type(self, if_name: str) -> InterfaceType:
        """
        Retrieve the type of an interface by its name.

        Args:
            if_name (str): The name of the interface.

        Returns:
            InterfaceType: The type of the interface if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT InterfaceType FROM Interfaces WHERE InterfaceName = ?", (if_name,))
            row = cursor.fetchone()
            if row:
                interface_type = InterfaceType(row[0])
                return interface_type
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' type: %s", e)
        return None

    def get_interface_id(self, if_name: str) -> int:
        """
        Retrieve the ID of an interface by its name.

        Args:
            if_name (str): The name of the interface.

        Returns:
            int: The ID of the interface if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Interfaces WHERE InterfaceName = ?", (if_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' ID: %s", e)
        return None

    def interface_exists(self, if_name: str) -> Result:
        """
        Check if an interface with the given name exists in the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface to check.

        Returns:
            Result: A Result object with the status and row ID of the existing interface.
            status: True = exists, otherwise False
            row_id: row-id of interface when status=true
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Interfaces WHERE InterfaceName = ?", (if_name,))
            self.connection.commit()
            existing_row = cursor.fetchone()
            
            if existing_row:
                return Result(status=True, row_id=existing_row[0])
            else:
                return Result(status=False, row_id=0)
        
        except sqlite3.Error as e:
            self.log.error("Error checking if interface exists: %s", e)
            return Result(status=False, row_id=0)

    def insert_interface(self, if_name, interface_type, shutdown_status=True) -> Result:
        """
        Insert data into the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface.
            interface_type (InterfaceType): The type of the interface.
            shutdown_status (bool, optional): True if the interface is shutdown, False otherwise.

        Returns:
            Result: A Result object with the status of the insertion and the row ID.
                    status = STATUS_OK success, STATUS_NOK otherwise
        """
        
        existing_result = self.interface_exists(if_name)
        
        if existing_result.status:
            return Result(status=STATUS_NOK, 
                        row_id=existing_result.row_id, 
                        reason=f"Interface: {if_name} already exists")

        try:
            self.log.debug(f"insert_interface() -> Interface: {if_name} -> Interface-Type: {interface_type.value} -> shutdown: {shutdown_status}")
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Interfaces (InterfaceName, InterfaceType, ShutdownStatus) VALUES (?, ?, ?)",
                (if_name, interface_type.value, shutdown_status)
            )
            
            self.connection.commit()
            
            self.log.debug("Data inserted into the 'Interfaces' table successfully.")
            
            return Result(status=STATUS_OK, row_id=cursor.lastrowid)
        
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Interfaces': %s", e)
            return Result(status=STATUS_NOK, row_id=0, reason=f"{e}")

    def delete_interface(self, if_name: str) -> Result:
        """
        Delete an interface from the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        try:
            existing_result = self.interface_exists(if_name)
            
            if existing_result.status:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Interfaces WHERE InterfaceName = ?", (if_name,))
                self.connection.commit()
                self.log.debug(f"Deleted interface '{if_name}' from the 'Interfaces' table.")
                return Result(status=STATUS_OK, row_id=0, reason=f"Interface '{if_name}' deleted successfully.")
            else:
                self.log.debug(f"Interface '{if_name}' does not exist.")
                return Result(status=STATUS_NOK, row_id=0, reason=f"Interface '{if_name}' does not exist.")
        except sqlite3.Error as e:
            self.log.error("Error deleting interface: %s", e)
            return Result(status=STATUS_NOK, row_id=0, reason=f"{e}")
    
    def update_interface_shutdown(self, interface_name: str, shutdown_status: bool) -> Result:
        """
        Update the shutdown status of an interface in the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface to update.
            shutdown_status (bool): True =  shutdown interface
                                    False = no shutdown interface     

        Returns:
            Result: A Result object with the status of the update.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            # Interface does not exist
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            cursor = self.connection.cursor()
            
            cursor.execute(
                "UPDATE Interfaces SET ShutdownStatus = ? WHERE InterfaceName = ?",
                (shutdown_status, interface_name)
            )
            
            self.connection.commit()
            
            self.log.debug(f"Shutdown status updated for interface: {interface_name}")
            
            return Result(status=STATUS_OK, row_id=existing_result.row_id)
        
        except sqlite3.Error as e:
            self.log.error(f"Error updating shutdown status for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=existing_result.row_id, reason=f"{e}")

    def update_interface_duplex(self, interface_name: str, duplex: str) -> Result:
        """
        Update the duplex setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to update.
            duplex (str): The new duplex setting.

        Returns:
            Result: A Result object with the status of the update.
                    - status:   STATUS_OK successful, STATUS_NOK otherwise
                    - row_id:   STATUS_OK row_id > 0, STATUS_NOK row_id = 0
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        interface_id = existing_result.row_id
        
        try:

            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM InterfaceSubOptions WHERE Interface_FK = ?", (interface_id,))
            sub_options_row = cursor.fetchone()

            if sub_options_row:
                # If an entry exists, update the duplex setting
                cursor.execute(
                    "UPDATE InterfaceSubOptions SET Duplex = ? WHERE Interface_FK = ?",
                    (duplex, interface_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO InterfaceSubOptions (Interface_FK, Duplex) VALUES (?, ?)",
                    (interface_id, duplex)
                )

            self.connection.commit()
            self.log.debug(f"Duplex setting updated for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(f"Error updating duplex setting for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=str(e))

    def update_interface_mac_address(self, interface_name: str, mac_address: str) -> Result:
        """
        Update the MAC address setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to update.
            mac_address (str): MAC address in the format xx:xx:xx:xx:xx:xx.

        Returns:
            Result: A Result object with the status of the update.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()  # Create a cursor object
            cursor.execute("SELECT ID FROM InterfaceSubOptions WHERE Interface_FK = ?", (interface_id,))
            sub_options_row = cursor.fetchone()

            if sub_options_row:
                cursor.execute(
                    "UPDATE InterfaceSubOptions SET MacAddress = ? WHERE Interface_FK = ?",
                    (mac_address, interface_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO InterfaceSubOptions (Interface_FK, MacAddress) VALUES (?, ?)",
                    (interface_id, mac_address)
                )

            self.connection.commit()
            self.log.debug(f"MAC address setting updated for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(f"Error updating MAC address setting for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=str(e))

    def update_interface_speed(self, interface_name: str, speed: str) -> Result:
        """
        Update the speed setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to update.
            speed (str): Speed setting, one of ['10', '100', '1000', '10000', 'auto'].

        Returns:
            Result: A Result object with the status of the update.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            self.log.error(f"Interface: {interface_name} does not exists.")
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM InterfaceSubOptions WHERE Interface_FK = ?", (interface_id,))
            
            sub_options_row = cursor.fetchone()

            if sub_options_row:
                cursor.execute(
                    "UPDATE InterfaceSubOptions SET Speed = ? WHERE Interface_FK = ?",
                    (speed, interface_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO InterfaceSubOptions (Interface_FK, Speed) VALUES (?, ?)",
                    (interface_id, speed)
                )

            self.connection.commit()
            self.log.debug(f"Speed {speed} setting updated for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(f"Error updating speed: {speed} setting for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=f"{e}")

    '''
                    INTERFACE-IP-ADDRESS DATABASE
    '''
            
    def insert_interface_inet_address(self, interface_name: str, ip_address: str, is_secondary: bool) -> Result:
        """
        Insert an IP address entry for an interface into the 'InterfaceIpAddress' table.

        Args:
            if_name (str): The name of the interface to associate the IP address with.
            ip_address (str): The IP address in the format IPv4 or IPv6 Address/Mask-Prefix.
            is_secondary (bool): True if the IP address is secondary, False otherwise.

        Returns:
            Result: A Result object with the status of the insertion.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            # Interface does not exist
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO InterfaceIpAddress (Interface_FK, IpAddress, SecondaryIp) VALUES (?, ?, ?)",
                (interface_id, ip_address, is_secondary)
            )

            self.connection.commit()
            self.log.debug(f"IP address {ip_address} inserted for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(f"Error inserting IP address for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=f"{e}")

    def delete_interface_inet_address(self, interface_name: str, ip_address: str) -> Result:
        """
        Delete the entire row associated with an IP address for an interface from the 'InterfaceIpAddress' table.

        Args:
            if_name (str): The name of the interface.
            ip_address (str): The IP address to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            # Interface does not exist
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM InterfaceIpAddress WHERE Interface_FK = ? AND IpAddress = ?",
                (interface_id, ip_address)
            )
            self.connection.commit()
            self.log.debug(f"IP address {ip_address} row deleted for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(f"Error deleting IP address for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=f"{e}")

    def _sub_option_row_exists(self, interface_fk: int) -> Result:
        """
        Check if a row with the given Interface_FK exists in the 'InterfaceSubOptions' table.

        Args:
            interface_fk (int): The foreign key (Interface_FK) to check.

        Returns:
            Result: A Result object with the 'row_id' field indicating the found 'ID' or 0 if not found.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM InterfaceSubOptions WHERE Interface_FK = ?", (interface_fk,))
            row = cursor.fetchone()
            return Result(status=True, row_id=row[0] if row else 0)
        except sqlite3.Error:
            return Result(status=True, row_id=0)

    '''
                    INTERFACE-SUB-OPTIONS DATABASE
    '''

    def interface_and_sub_option_exist(self, interface_name: str) -> Result:
        """
        Check if an interface with the given name exists in the 'Interfaces' table and if a corresponding row exists in
        the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to check.

        Returns:
            Result: A Result object indicating the outcome of the checks.
                    'status' : True if both exist, False otherwise
                    'row_id' : If exist, row_id > 0, 0 if not found
                    'result' : Result of SQL query
        """
        interface_exists_result = self.interface_exists(interface_name)

        if not interface_exists_result.status:
            return Result(status=False, reason=f"Interface: {interface_name} doesn't exist")

        sub_option_row_result = self._sub_option_row_exists(interface_exists_result.row_id)

        if sub_option_row_result.row_id:
            return Result(status=True, row_id=sub_option_row_result.row_id)
        else:
            return Result(status=False, reason="Interface exists, but no corresponding row in InterfaceSubOptions")

    def update_interface_proxy_arp(self, interface_name: str, status: bool) -> Result:
        """
        Update the Proxy ARP setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to update.
            status (bool): True to enable Proxy ARP, False to disable it.

        Returns:
            Result: A Result object with the status of the update.
                    'status' : STATUS_OK if successful, STATUS_NOK otherwise
                    'row_id' : If exists, row_id > 0
                    'result' : Result of SQL query
        """
        
        if_exists = self.interface_exists(interface_name)
        
        if not if_exists.status:
            return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=if_exists.reason)
        
        if_sub_opt = self.interface_and_sub_option_exist(interface_name)
        
        if not if_sub_opt.status:
            insert_if_sub_option = self._insert_default_row_in_interface_sub_option(interface_name)
            if not insert_if_sub_option.status:
                return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=insert_if_sub_option.reason)
        
        try:

            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE InterfaceSubOptions SET ProxyArp = ? WHERE Interface_FK = ?",
                (status, if_exists.row_id)
            )

            self.connection.commit()
            self.log.debug(f"update_interface_proxy_arp() -> Proxy ARP setting updated for interface: {interface_name}")
            return Result(STATUS_OK, row_id=if_sub_opt.row_id)

        except sqlite3.Error as e:
            self.log.error(f"update_interface_proxy_arp() -> Error updating Proxy ARP setting for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=if_sub_opt.row_id, reason=str(e))

    def update_interface_drop_gratuitous_arp(self, interface_name: str, status: bool) -> Result:
        """
        Update the 'Drop Gratuitous ARP' setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to update.
            status (bool): True to enable 'Drop Gratuitous ARP,' False to disable it.

        Returns:
            Result: A Result object with the status of the update.
                    'status' : STATUS_OK if successful, STATUS_NOK otherwise
                    'row_id' : If exists, row_id > 0
                    'result' : Result of SQL query
        """
        
        # Check if the interface exists
        if_exists = self.interface_exists(interface_name)
        
        if not if_exists.status:
            return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=if_exists.reason)
        
        # Check if the sub-option row exists
        if_sub_opt = self.interface_and_sub_option_exist(interface_name)
        
        if not if_sub_opt.status:
            # If the sub-option row doesn't exist, insert a default row
            insert_if_sub_option = self._insert_default_row_in_interface_sub_option(interface_name)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE InterfaceSubOptions SET DropGratuitousArp = ? WHERE Interface_FK = ?",
                (status, if_exists.row_id)
            )

            self.connection.commit()
            self.log.debug(f"update_interface_drop_gratuitous_arp() -> 'Drop Gratuitous ARP' setting updated for interface: {interface_name}")
            return Result(STATUS_OK, row_id=if_sub_opt.row_id)

        except sqlite3.Error as e:
            self.log.error(f"update_interface_drop_gratuitous_arp() -> Error updating 'Drop Gratuitous ARP' setting for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=if_sub_opt.row_id, reason=str(e))

    def update_interface_static_arp(self, interface_name: str, ip_address: str, mac_address: str, encapsulation: str) -> Result:
        """
        Create a default entry in the 'InterfaceStaticArp' table if it does not already exist, or update it if it exists.

        Args:
            if_name (str): The name of the interface to associate the static ARP record with.
            ip_address (str): The IP address in IPv4 or IPv6 format.
            mac_address (str): The MAC address in the format: xx:xx:xx:xx:xx:xx.
            encapsulation (str): The encapsulation type, e.g., 'arpa' or 'TBD'.

        Returns:
            Result: A Result object with the status of the operation.
        """
        self.log.debug(f"update_interface_static_arp() If: {interface_name} , IP: {ip_address} , mac: {mac_address} , encap: {encapsulation}")
        try:
            # Check if the interface exists and get its ID
            interface_exists_result = self.interface_exists(interface_name)
            if not interface_exists_result.status:
                return Result(STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM InterfaceStaticArp WHERE Interface_FK = ? AND IpAddress = ?",
                (interface_exists_result.row_id, ip_address)
            )
            existing_entry = cursor.fetchone()

            if existing_entry:
                self.log.debug(f"update_interface_static_arp() -> Entry Exist, Updating IP: {ip_address} -> Mac: {mac_address}")
                cursor.execute(
                    "UPDATE InterfaceStaticArp SET MacAddress = ?, Encapsulation = ? WHERE ID = ?",
                    (mac_address, encapsulation, existing_entry[0])
                )
                self.connection.commit()
                self.log.debug(f"Static ARP entry updated for interface: {interface_name}")
            else:
                self.log.debug(f"update_interface_static_arp() -> Entry NOT Found, inserting IP: {ip_address} -> Mac: {mac_address}")
                cursor.execute(
                    "INSERT INTO InterfaceStaticArp (Interface_FK, IpAddress, MacAddress, Encapsulation) VALUES (?, ?, ?, ?)",
                    (interface_exists_result.row_id, ip_address, mac_address, encapsulation)
                )
                self.connection.commit()
                self.log.debug(f"Static ARP entry added for interface: {interface_name}")

            return Result(STATUS_OK, row_id=existing_entry[0] if existing_entry else cursor.lastrowid)

        except sqlite3.Error as e:
            self.log.error(f"Error creating or updating static ARP entry for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=0, reason=str(e))

    def delete_interface_static_arp(self, interface_name: str, ip_address: str) -> Result:
        """
        Delete a static ARP record from the 'InterfaceStaticArp' table.

        Args:
            if_name (str): The name of the interface to associate with the static ARP record.
            ip_address (str): The IP address to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        self.log.debug(f"delete_interface_static_arp() If: {interface_name} , IP: {ip_address}")
        
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id
            
            cursor = self.connection.cursor()
            
            self.log.debug(f"delete_interface_static_arp() Deleting Row -> Interface-FK: {interface_name} , IP: {ip_address}")
  
            cursor.execute(
                "DELETE FROM InterfaceStaticArp WHERE Interface_FK = ? AND IpAddress = ?",
                (interface_id, ip_address)
            )
            
            self.connection.commit()
            
            self.log.debug(f"Static ARP record deleted for interface: {interface_name}")
            
            return Result(STATUS_OK, row_id=interface_id)
        
        except sqlite3.Error as e:
            self.log.error(f"Error deleting static ARP record for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=interface_id, reason=str(e))

    def insert_interface_bridge_group(self, interface_name: str, bridge_name: str) -> Result:
        """
        Insert an interface into a bridge group in the 'BridgeGroups' table.

        Args:
            interface_name (str): The name of the interface.
            bridge_name (str): The name of the bridge group.

        Returns:
            Result: A Result object with the status of the insertion.
        """
        interface_result = self.interface_exists(interface_name)
        
        if not interface_result.status:
            self.log.debug(f"insert_interface_bridge_group() -> interface: {interface_name} does not exist, Exiting")
            return Result(STATUS_NOK, reason=f"Interface: {interface_name} does not exist")

        bridge_result = self.bridge_exist_db(bridge_name)

        if not bridge_result.status:
            self.log.debug(f"insert_interface_bridge_group() -> Bridge group: {bridge_name} does not exist, Exiting")
            return Result(STATUS_NOK, reason=f"Bridge group: {bridge_name} does not exist")

        interface_id = interface_result.row_id
        
        bridge_id = bridge_result.row_id

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO BridgeGroups (Interface_FK, BridgeGroups_FK) VALUES (?, ?)",
                (interface_id, bridge_id)
            )
            row_id = cursor.lastrowid
            self.connection.commit()
            return Result(STATUS_OK, row_id=row_id, reason="Interface added to the bridge group successfully")
        
        except sqlite3.Error as e:
            error_message = f"Error inserting data into 'BridgeGroups': {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=error_message)

    def delete_interface_bridge_group(self, interface_name: str, bridge_name: str) -> Result:
        """
        Remove an interface from a bridge group in the 'BridgeGroups' table.

        Args:
            if_name (str): The name of the interface.
            bridge_name (str): The name of the bridge group.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        # Look up the interface and bridge group by name
        interface_result = self.interface_exists(interface_name)
        
        if not interface_result.status:
            return Result(STATUS_NOK, reason=f"Interface: {interface_name} does not exist")

        bridge_result = self.bridge_exist_db(bridge_name)

        if not bridge_result.status:
            return Result(STATUS_NOK, reason=f"Bridge group: {bridge_name} does not exist")

        interface_id = interface_result.row_id
        bridge_id = bridge_result.row_id

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM BridgeGroups WHERE Interface_FK = ? AND BridgeGroups_FK = ?",
                (interface_id, bridge_id)
            )
            self.connection.commit()
            return Result(STATUS_OK, reason="Interface removed from the bridge group successfully")
        
        except sqlite3.Error as e:
            error_message = f"Error deleting data from 'BridgeGroups': {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def _insert_default_row_in_interface_sub_option(self, interface_name: str) -> Result:
        """
        Insert a default row into the InterfaceSubOptions table if it does not already exist.

        Args:
            if_name (str): The name of the network interface.

        Returns:
            Result: An instance of Result if the row is successfully or not inserted.
        """
        try:
            cursor = self.connection.cursor()

            interface_exists_result = self.interface_exists(interface_name)
            if not interface_exists_result.status:
                return Result(status=False, reason=f"Interface:{interface_name} does not exists")

            cursor.execute("SELECT ID FROM InterfaceSubOptions WHERE Interface_FK = ?", (interface_exists_result.row_id,))
            existing_row = cursor.fetchone()

            if existing_row is not None:
                return Result(status=False, reason="Row already exists")

            cursor.execute("INSERT INTO InterfaceSubOptions (Interface_FK) VALUES (?)", (interface_exists_result.row_id,))
            row_id = cursor.lastrowid  # Get the inserted row's ID
            self.connection.commit()

            return Result(status=True, row_id=row_id, reason="Row inserted successfully")

        except sqlite3.Error:
            return Result(status=False, reason="Database error")

    '''
                        INTERFACE-RENAME-ALIAS
    '''

    def update_interface_alias(self, initial_interface: str, alias_interface: str) -> Result:
        """
            Update or create an alias for an initial interface.

            Args:
                initial_interface (str): The name of the initial interface.
                alias_interface (str): The name of the alias interface.

            Returns:
                Result: A Result object with the following fields:
                - status (bool): STATUS_OK if the alias was updated or created successfully, STATUS_NOK otherwise.
                - row_id (int): The row ID of the updated or created alias entry.

            Raises:
                sqlite3.Error: If there is an error with the database query.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO RenameInterface (InitialInterface, AliasInterface)
                VALUES (?, ?)
            """, (initial_interface, alias_interface))

            self.connection.commit()

            cursor.execute("SELECT ID FROM RenameInterface WHERE InitialInterface = ?", (initial_interface,))
            row_id = cursor.fetchone()[0]

            return Result(status=STATUS_OK, row_id=row_id)
        
        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=e)

    def is_initial_interface_alias_exist(self, initial_interface: str) -> Result:
        """
        Check if an alias exists for the given initial interface.

        Args:
            initial_interface (str): The name of the initial interface to check.

        Returns:
            Result: A Result object with the following fields:
            - status (bool): True if an alias exists for the initial interface, False otherwise.
            - row_id (int, optional): The row ID of the alias entry if an alias exists, or None if no alias exists.
            - reason (str, optional): A reason for the result, which may include additional information.
            - result (str, optional): The alias name if an alias exists, or None if no alias exists.

        Raises:
            sqlite3.Error: If there is an error with the database query.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT AliasInterface, ID FROM RenameInterface WHERE InitialInterface = ?", (initial_interface,))
            row = cursor.fetchone()

            if row is not None:
                alias_name, row_id = row
                return Result(status=True, alias_name=alias_name, row_id=row_id)
            else:
                return Result(status=False, row_id=None, result=alias_name)
        
        except sqlite3.Error as e:
            return Result(status=False, alias_name=None, row_id=None, reason=str(e))

