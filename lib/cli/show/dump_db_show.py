from tabulate import tabulate
from lib.db.sqlite_db.router_shell_db import RouterShellDB as DB

class DbDumpShow:
    
    def __init__(self):
        """
        Initializes the DbDumpShow with a connection to the SQLite database.
        """
        self._connection_cursor = DB().connection.cursor()
        print(f"DbDumpShow()->init()->{self._connection_cursor.__str__()}")

    def _fetch_tables(self, search_term: str = ''):
        """
        Fetches the list of all table names in the database, optionally filtered by a search term.

        Args:
            search_term (str): A term to filter table names by.

        Returns:
            list: A list of table names that match the search term.
        """
        cursor = self._connection_cursor
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        
        if search_term:
            search_term = f"%{search_term}%"
            query += " AND name LIKE ?"
            cursor.execute(query, (search_term,))
        else:
            query += ";"
            cursor.execute(query)
        
        return cursor.fetchall()

    def _fetch_schema(self, table_name: str):
        """
        Fetches the schema of a specific table.

        Args:
            table_name (str): The name of the table.

        Returns:
            list: A list of schema information for the table.
        """
        cursor = self._connection_cursor
        cursor.execute(f"PRAGMA table_info({table_name});")
        return cursor.fetchall()

    def _fetch_data(self, table_name: str):
        """
        Fetches the data of a specific table.

        Args:
            table_name (str): The name of the table.

        Returns:
            tuple: A tuple containing the column names and rows of data.
        """
        cursor = self._connection_cursor
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return column_names, rows

    def _print_schema(self, table_name: str, schema):
        """
        Prints the schema of a table in a human-readable format.

        Args:
            table_name (str): The name of the table.
            schema (list): The schema information to print.
        """
        print(f"\nSchema: {table_name}")
        schema_table = [["Column", "Type", "Not Null", "Default Value"]]
        schema_table.extend([[col[1], col[2], col[3], col[4]] for col in schema])
        print(tabulate(schema_table, headers='firstrow', tablefmt='grid'))

    def _print_data(self, table_name: str, column_names, rows):
        """
        Prints the data of a table in a human-readable format.

        Args:
            table_name (str): The name of the table.
            column_names (list): The column names of the table.
            rows (list): The rows of data to print.
        """
        print(f"\nTable: {table_name}")
        data_table = [column_names] + rows
        try:
            print(tabulate(data_table, headers='firstrow', tablefmt='grid'))
        except Exception as e:
            print(f"Error printing data for table {table_name}: {e}")

    def dump_db(self, include_schema: bool = False, search_term: str = ''):
        """
        Dumps the contents of the SQLite database to the console in a human-readable format.
        Optionally includes schema information and filters tables based on a search term.

        Args:
            include_schema (bool): If True, includes schema information in the output.
            search_term (str): A term to filter table names by.
        """
        tables = self._fetch_tables(search_term)
        
        if not tables:
            print("No tables found in the database.")
            return

        for (table_name,) in tables:
            if include_schema:
                try:
                    schema = self._fetch_schema(table_name)
                    self._print_schema(table_name, schema)
                except Exception as e:
                    print(f"Error fetching schema for table {table_name}: {e}")

            try:
                column_names, rows = self._fetch_data(table_name)
                self._print_data(table_name, column_names, rows)
            except Exception as e:
                print(f"Error fetching data for table {table_name}: {e}")
