import sqlite3
import logging

from lib.network_manager.interface import InterfaceType


class RouterShellDatabaseConnector:
    def __init__(self, sql_file_path):
        self.log = logging.getLogger(self.__class__.__name__)
        self.sql_file_path = sql_file_path
        self.connection = None

    def create_database(self):
        try:
            # Connect to an in-memory database
            self.connection = sqlite3.connect(':memory:')
            cursor = self.connection.cursor()

            # Read the SQL file
            with open(self.sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()

            # Execute the SQL script to create tables and populate data
            cursor.executescript(sql_script)

            # Commit the changes
            self.connection.commit()

            print("In-memory database created successfully.")

        except sqlite3.Error as e:
            print("Error:", e)

    def close_connection(self):
        if self.connection:
            self.connection.close()

def insert_interface(self, id, if_name, interface_type: InterfaceType, if_name_alias=None):
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

    def insert_bridge(self, id, interface_fk, bridge_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Bridges (ID, Interface_FK, BridgeName) VALUES (?, ?, ?)",
                (id, interface_fk, bridge_name)
            )
            self.connection.commit()
            self.log.info("Data inserted into the 'Bridges' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Bridges': %s", e)

    def insert_vlan(self, id, vlan_interfaces_fk, vlan_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Vlans (ID, VlanInterfaces_FK, VlanName) VALUES (?, ?, ?)",
                (id, vlan_interfaces_fk, vlan_name)
            )
            self.connection.commit()
            self.log.info("Data inserted into the 'Vlans' table successfully.")
        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Vlans': %s", e)

    def insert_vlan_interface(self, id, vlan_name, interface_fk, bridge_fk):
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

    def insert_nat(self, id, nat_pool_name, interface_fk):
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

    def insert_nat_direction(self, id, nat_fk, interface_fk, direction):
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

    def insert_dhcp(self, id, interface_fk, dhcp_poolname):
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

    def insert_subnet(self, id, dhcp_fk, ip_subnet):
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

    def insert_pools(self, id, subnet_fk, ip_address_start, ip_address_end, ip_subnet):
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

    def insert_options_pools(self, id, pools_fk, dhcp_options, dhcp_value):
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

    def insert_options_global(self, id, dhcp_fk, dhcp_options, dhcp_value):
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

    def insert_reservations(self, id, subnet_fk, mac_address, ip_address):
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

    def insert_options_reservations(self, id, pool_reservations_fk, dhcp_options, dhcp_value):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO OptionsReservations (id, PoolReservations_FK, DhcpOptions, DhcpValue) VALUES (?, ?, ?, ?)",
                (id, pool_reservations_fk, dhcp_options, dhcp_value)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            self.log.error("Error inserting into 'OptionsReservations': %s", e)

    def get_interface_id(self, if_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Interfaces WHERE IfName = ?", (if_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' ID: %s", e)
        return None

    def get_bridge_id(self, bridge_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Bridges WHERE BridgeName = ?", (bridge_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Bridges' ID: %s", e)
        return None

    def get_vlan_interfaces_id(self, vlan_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM VlanInterfaces WHERE VlanName = ?", (vlan_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'VlanInterfaces' ID: %s", e)
        return None

    def get_nat_id(self, nat_pool_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Nats WHERE NatPoolName = ?", (nat_pool_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Nats' ID: %s", e)
        return None

    def get_dhcp_id(self, dhcp_poolname):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM DHCP WHERE DhcpPoolname = ?", (dhcp_poolname,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'DHCP' ID: %s", e)
        return None

    def get_subnet_id(self, ip_subnet):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM Subnet WHERE IpSubnet = ?", (ip_subnet,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Subnet' ID: %s", e)
        return None

    def get_pools_id(self, ip_address_start, ip_address_end):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM Pools WHERE IpAddressStart = ? AND IpAddressEnd = ?", (ip_address_start, ip_address_end))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Pools' ID: %s", e)
        return None

    def get_options_pools_id(self, dhcp_options, dhcp_value):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM OptionsPools WHERE DhcpOptions = ? AND DhcpValue = ?", (dhcp_options, dhcp_value))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'OptionsPools' ID: %s", e)
        return None

    def get_options_global_id(self, dhcp_options, dhcp_value):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM OptionsGlobal WHERE DhcpOptions = ? AND DhcpValue = ?", (dhcp_options, dhcp_value))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'OptionsGlobal' ID: %s", e)
        return None

    def get_reservations_id(self, mac_address, ip_address):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM Reservations WHERE MacAddress = ? AND IPAddress = ?", (mac_address, ip_address))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Reservations' ID: %s", e)
        return None

    def get_options_reservations_id(self, dhcp_options, dhcp_value):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM OptionsReservations WHERE DhcpOptions = ? AND DhcpValue = ?", (dhcp_options, dhcp_value))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'OptionsReservations' ID: %s", e)
        return None
                 
