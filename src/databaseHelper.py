import sqlite3
from typing import Any, TypedDict

class DatabaseColumn(TypedDict):
    name: str
    keyType: str

class DatabaseKeyValuePair(TypedDict):
    row: str
    value: Any


class Database:

    def __init__(self, database_path: str):

        '''
        Loads the databases
        Creates tables if needed
        '''
        print("****** DB HELPER *********")
        print("New instance of Database class has been created!")
        print("****** DB HELPER *********")
        self.database = sqlite3.connect(database_path, check_same_thread=False)
    
    def create_table_if_not_exists(self, table_name: str, columns: dict[str, str])->None:

        command = f"CREATE TABLE IF NOT EXISTS {table_name}("
        for col in columns.keys():
            command += f"{col} {columns[col]}, "
        command = command[:-2]
        command += ")"
        print(f"Command is: {command}")
        self.execute_command(command)

        self.database.commit()

    def execute_command(self, command: str, params: tuple[Any, ...] = ())->None:
        """
        Creates a new cursor, executes the command, and closes the cursor.
        """
        print("DB HELPER - cursor am")
        print(f"DB HELPER: Command: {command}")
        print(f"DB HELPER: Params: {params}")
        cursor = self.database.cursor()
        cursor.execute(command, params)
        cursor.close()
    def execute_command_and_return_cursor(self, command: str, params: tuple[Any, ...] = ())-> sqlite3.Cursor:
        """
        Creates a new cursor, executes the command, BUT DOES NOT CLOSE THE CURSOR.
        The cursor will have to be MANUALLY closed to prevent memory leak.
        """
        print("DB HELPER - return cursor")
        print(f"DB HELPER: Command: {command}")
        print(f"DB HELPER: Params: {params}")
        cursor = self.database.cursor()
        cursor.execute(command, params)
        return cursor

    def read_row_from_table(self, table: str, queryKey: str, queryValue: Any, cols:list[str])->dict[str, Any]|None:
        """
        Fetches row from table. Returns NONE if target not found.
        Returns data in RV(row value) pairs
        """
        command: str = f"SELECT * from {table} WHERE {queryKey} = ?"

        cursor = self.execute_command_and_return_cursor(command, (queryValue,))
    
        row_data: tuple[Any, ...] | None = cursor.fetchone()
        if row_data == None:
            print("DB HELPER: Read failed: no data matches query")
            return None

        dict_data:dict[str, Any] = {}
        i = 0

        for k in cols:
            dict_data[k] = row_data[i]
            i += 1
        

        return dict_data

    def change_row_in_table(self, table: str, values: dict[str, Any], queryKey: str, queryValue: Any)->None:
        """
        Changes data of a row in the database

        Args:
            table (str): table to target
            values (list[DatabaseKeyValuePair]): pair between row name and value
            queryKey (str): name of row to search
            queryValue (Any): value of row to search
        Returns:
            None
        """
        set_command = ""
        for i in values.keys():
            set_command += i + " = ?, "
        set_command = set_command[:-2] # strip comma and trailing space at the end
        command = f'''
        UPDATE {table}
        SET {set_command}
        WHERE {queryKey} = ?
        '''

        print(f"Command: {command}")

        parameters_list = []
        for i in values.keys():
            parameters_list.append(values[i])
        
        parameters = (*parameters_list, queryValue)
        print(f"Parameter list: {parameters}")

        self.execute_command(command, parameters)

        self.database.commit()

    def add_new_row(self, table: str, values: dict[str, Any])->int | None:
        """
        Adds a new row a specific table in the database.

        Args:
            table (str): Name of the table to target
            keys: (list[str]): List of the rows
            values: (list[Any]): Value for each row
        Returns:
            None
        """




        question_marks = ('?, ' * (len(values.keys())))[:-2] 
        print(F"Question marks: {question_marks}")

        command = f'''
        INSERT INTO {table} {str(tuple(values.keys()))}
        VALUES ({question_marks})
        '''
        
        print(f"Command: {command}")

        c = self.execute_command_and_return_cursor(command, tuple(values.values()))
        lr = c.lastrowid
        c.close()

        self.database.commit()
        return lr
    
    def delete_row(self, table: str, queryKey: str, queryValue: Any)->None:
        """
        Deletes row from a specific table in the database.

        Args:
            table (str): Name of the table to target
            queryKey (str): Name of the column to select
            queryValue (str): Actual value that SQL should search for
        Returns:
            None
        """
        command = f'''
        DELETE FROM {table}
        WHERE {queryKey} = ?
        '''
        print(f"Command: {command}")

        self.execute_command(command, (queryValue,))

        self.database.commit()
    