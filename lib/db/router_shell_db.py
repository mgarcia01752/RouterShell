import sqlite3
import logging
import os
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_manager import InterfaceType

class InsertResult:
    
    def __init__(self, status: bool, row_id:int, result:str=None):

        self.status = status
        self.row_id = row_id
        self.result = result

class UpdateResult:
    """
    Represents the result of an insert operation into the database.

    Attributes:
        status (bool): The status of the insert operation. True for success (STATUS_OK), False for failure (STATUS_NOK).
        row_id (int): The row ID of the inserted item in the database. -1 if the insert operation failed.
    """

    def __init__(self, status: bool, result: str=None):
        """
        Initialize an InsertResult object.

        Args:
            status (bool): The status of the insert operation. STATUS_OK is success, STATUS_NOK for failure.
            result (str): 
        """
        self.status = status
        self.result = result

class RouterShellDatabaseConnector:
    connection = None
    
    ROUTER_SHELL_DB = 'routershell.db'
    ROUTER_SHELL_SQL_STARTUP = 'db_schema.sql'

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.log.info(f"__init__() - DB Connection Status -> {self.connection}")
        self.db_file_path = os.path.join(os.path.dirname(__file__), self.ROUTER_SHELL_DB)
        self.sql_file_path = os.path.join(os.path.dirname(__file__), self.ROUTER_SHELL_SQL_STARTUP)
        
        if not self.connection:
            self.log.info(f"Connecting to DB {self.ROUTER_SHELL_DB}")
            self.create_database()
        else:
            self.log.info(f"Already Connected to DB {self.ROUTER_SHELL_DB}")


    def create_database(self):
        """
        Create an SQLite database file and populate it with tables and data from an SQL file.
        """
        
        self.log.info(f"create_database()")
        
        try:
            # Connect to the SQLite database file
            self.connection = sqlite3.connect(self.db_file_path)
            cursor = self.connection.cursor()

            # Read the SQL file
            with open(self.sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()

            # Execute the SQL script to create tables and populate data
            cursor.executescript(sql_script)

            # Commit the changes
            self.connection.commit()

            self.log.info("SQLite database created successfully.")

        except sqlite3.Error as e:
            print("Error:", e)

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()

    def insert_interface(self, id: int, if_name: str, interface_type: InterfaceType, if_name_alias: str = None):
        """
        Insert data into the 'Interfaces' table.

        Args:
            id (int): The unique ID of the interface.
            if_name (str): The name of the interface.
            interface_type (InterfaceType): The type of the interface.
            if_name_alias (str, optional): An alias name for the interface.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Interfaces (ID, IfName, IfNameAlias, InterfaceType) VALUES (?, ?, ?, ?)",
                (id, if_name, if_name_alias, interface_type.value)
            )
            self.connection.commit()
            self.log.info("Data inserted into the 'Interfaces' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Interfaces': %s", e)

    def insert_bridge(self, id: int, bridge_name: str, interface_fk: int = -1) -> InsertResult:
        """
        Insert data into the 'Bridges' table.

        Args:
            id (int): The unique ID of the bridge.
            bridge_name (str): The name of the bridge.
            interface_fk (int, optional): The foreign key referencing an interface.

        Returns:
            InsertResult: An instance of InsertResult containing the status and row ID.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Bridges (ID, Interface_FK, BridgeName) VALUES (?, ?, ?)",
                (id, interface_fk, bridge_name)
            )
            self.connection.commit()
            self.log.info("Data inserted into the 'Bridges' table successfully.")
            row_id = cursor.lastrowid
            return InsertResult(STATUS_OK, row_id)
        except sqlite3.Error as e:
            rtn = "Error inserting data into 'Bridges': %s", e
            self.log.error(rtn)
            return InsertResult(STATUS_NOK, -1, rtn)


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

    def insert_vlan(self, vlanid: int, vlan_name: str, vlan_interfaces_fk: int = -1):
        """
        Insert data into the 'Vlans' table.

        Args:
            vlanid (int): The unique ID of the VLAN.
            vlan_name (str): The name of the VLAN.
            vlan_interfaces_fk (int, optional): The foreign key referencing VLAN interfaces.

        Returns:
            int: The row ID of the inserted VLAN.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        self.log.info(f"insert_vlan() -> vlanid: {vlanid}, vlan-if-fkey: {vlan_interfaces_fk}, vlan-name: {vlan_name}")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Vlans (VlanID, VlanInterfaces_FK, VlanName) VALUES (?, ?, ?)",
                (vlanid, vlan_interfaces_fk, vlan_name)
            )
            
            self.connection.commit()
            self.log.info("Data inserted into the 'Vlans' table successfully.")
            return cursor.lastrowid  # Return the row ID
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Vlans': %s", e)
            return -1

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
            self.log.info(f"VLAN Name -> {vlan_name} of VlanID -> {vlan_id} updated successfully.")
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
            self.log.info(f"Description of VLAN {vlan_id} updated successfully.")
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
            self.log.info("Data inserted into the 'VlanInterfaces' table successfully.")
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

    def insert_nat(self, id: int, nat_pool_name: str, interface_fk: int):
        """
        Insert data into the 'Nats' table.

        Args:
            id (int): The unique ID of the NAT.
            nat_pool_name (str): The name of the NAT pool.
            interface_fk (int): The foreign key referencing an interface.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Nats (ID, NatPoolName, Interface_FK) VALUES (?, ?, ?)",
                (id, nat_pool_name, interface_fk)
            )
            self.connection.commit()
            self.log.info("Data inserted into the 'Nats' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Nats': %s", e)

    def insert_nat_direction(self, id: int, nat_fk: int, interface_fk: int, direction: str):
        """
        Insert data into the 'NatDirections' table.

        Args:
            id (int): The unique ID of the NAT direction.
            nat_fk (int): The foreign key referencing a NAT.
            interface_fk (int): The foreign key referencing an interface.
            direction (str): The direction of the NAT.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO NatDirections (ID, NAT_FK, INTERFACE_FK, Direction) VALUES (?, ?, ?, ?)",
                (id, nat_fk, interface_fk, direction)
            )
            self.connection.commit()
            self.log.info("Data inserted into the 'NatDirections' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'NatDirections': %s", e)

    def insert_dhcp(self, id: int, interface_fk: int, dhcp_poolname: str):
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
            self.log.info("Data inserted into the 'DHCP' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'DHCP': %s", e)

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
            self.log.info("Data inserted into the 'Subnet' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Subnet': %s", e)

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
            self.log.info("Data inserted into the 'Pools' table successfully.")
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
            self.log.info("Data inserted into the 'OptionsPools' table successfully.")
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
            self.log.info("Data inserted into the 'OptionsGlobal' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'OptionsGlobal': %s", e)

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
            self.log.info("Data inserted into the 'Reservations' table successfully.")
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
            self.log.info("Data inserted into the 'OptionsReservations' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'OptionsReservations': %s", e)

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
            cursor.execute("SELECT ID FROM Interfaces WHERE IfName = ?", (if_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' ID: %s", e)
        return None

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
            self.log.error("Error retrieving 'Bridges' ID: %s", e)
        return None

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

    def get_nat_id(self, nat_pool_name: str) -> int:
        """
        Retrieve the ID of a NAT by its pool name.

        Args:
            nat_pool_name (str): The name of the NAT pool.

        Returns:
            int: The ID of the NAT if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Nats WHERE NatPoolName = ?", (nat_pool_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Nats' ID: %s", e)
        return None

    def get_dhcp_id(self, dhcp_poolname: str) -> int:
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
            cursor.execute("SELECT InterfaceType FROM Interfaces WHERE IfName = ?", (if_name,))
            row = cursor.fetchone()
            if row:
                interface_type = InterfaceType(row[0])
                return interface_type
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' type: %s", e)
        return None

    def get_nat_directions(self, nat_fk: int) -> list:
        """
        Retrieve the directions of a NAT by its foreign key.

        Args:
            nat_fk (int): The foreign key referencing a NAT.

        Returns:
            list: A list of directions for the NAT if found, or an empty list if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        directions = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT Direction FROM NatDirections WHERE NAT_FK = ?", (nat_fk,))
            rows = cursor.fetchall()
            if rows:
                directions = [row[0] for row in rows]
        except sqlite3.Error as e:
            self.log.error("Error retrieving NAT directions: %s", e)
        return directions

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
