import src.config as CONFIG
import sqlite3
from typing import NoReturn
from src.types import *

class DatabaseProvider:

    def __init__(self):
        self.load_databases()
        self.database_migration()

    def database_migration(self):
        print("Database migrate 2 keys")
        try:
            c = self.user_data_database_db.cursor()
            c.execute("ALTER TABLE users ADD COLUMN publicKey TEXT")
            c.execute("ALTER TABLE users ADD COLUMN privateKey TEXT")
            c.execute("ALTER TABLE users ADD COLUMN iv TEXT")

            c.close()
            self.user_data_database_db.commit()
        except Exception as e:
            print("Migration failed with following error:", e)
        print("Database finish migrating 2 keys")

    def load_databases(self):

        self.user_data_database_db = sqlite3.connect(f"{CONFIG.ABSOLUTE_PATH}databases/users.db", check_same_thread=False)


        self.themes_database_db = sqlite3.connect(f"{CONFIG.ABSOLUTE_PATH}databases/themes.db", check_same_thread=False)

        c = self.user_data_database_db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(31),
            favorites TEXT NOT NULL,
            ownedThemes TEXT NOT NULL,
            password VARCHAR(60),
            publicKey TEXT,
            privateKey TEXT,
            iv TEXT
            
                                        )
        ''')
        c.close()
        c = self.themes_database_db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY,
            themeName VARCHAR(255),
            description VARCHAR(2047),
            data TEXT NOT NULL,
            author TEXT NOT NULL,
            stars INT NOT NULL
                                        )
        ''')
        c.close()
    def read_authentication_data_for_user_or_id(self, *, user: str | None = None, id: int | None = None) -> AuthenticationDataReturnType | None | NoReturn:
        """
        Reads user data for specific user (by username or ID)
        ID is preferred because it is 10x faster.
        """

        if (user == None and id == None):
            raise ValueError("User and ID == null. One must not be null for indexing")
        if (user != None and id != None):
            raise ValueError("One must be none. Only one is needed for indexing")
        c = self.user_data_database_db.cursor()
        if user:
            
            c.execute(f'SELECT * FROM users WHERE username = ?', (user,))

        else:
            c.execute(f'SELECT * FROM users WHERE id = ?', (id,))

        user_data: tuple[int, str, str, str, str] = c.fetchone()
        c.close()
        if user_data == None: return None
        print(f"User data: {user_data}")
        # Index: id = 0, username = 1, favorites = 2, ownedThemes = 3, password = 4
        return {
            "id": user_data[0],
            "username": user_data[1],
            "favorites": user_data[2],
            "ownedThemes": user_data[3],
            "password": user_data[4],
            "publicKey": user_data[5],
            "privateKey": user_data[6],
            "iv": user_data[7]
        }
    def change_authentication_data_for_name_or_id(self, *, user: str | None = None, id: int | None = None, newData: AuthenticationDataReturnType):
        if (user == None and id == None):
            raise ValueError("User and ID == null. One must not be null for indexing")
        if (user != None and id != None):
            raise ValueError("One must be none. Only one is needed for indexing")
        c = self.user_data_database_db.cursor()
        if id:
            c.execute('''
            UPDATE users
            SET username = ?, favorites = ?, ownedThemes = ?, password = ?, publicKey = ?, privateKey = ?, iv = ?
            WHERE id = ?
            ''', (newData["username"], newData["favorites"], newData["ownedThemes"], newData["password"], newData["publicKey"], newData["privateKey"], newData["iv"], id))
        else:
            c.execute('''
            UPDATE users
            SET username = ?, favorites = ?, ownedThemes = ?, password = ?, publicKey = ?, privateKey = ?, iv = ?
            WHERE username = ?
            ''', (newData["username"], newData["favorites"], newData["ownedThemes"], newData["password"], newData["publicKey"], newData["privateKey"], newData["iv"], newData["username"]))
        c.close()
        self.user_data_database_db.commit()

    def read_theme_data_for_name_or_id(self, *, name: str | None = None, id: int | None = None) -> ThemeDataReturnType | None | NoReturn:
        """
        Reads user data for specific user (by username or ID)
        ID is preferred because it is 10x faster.
        """
        
        if (name == None and id == None):
            raise ValueError("Name and ID == null. One must not be null for indexing")
        if (name != None and id != None):
            raise ValueError("One must be none. Only one is needed for indexing")
        c = self.themes_database_db.cursor()
        if name:
            c.execute(f'SELECT * FROM themes WHERE themeName = ?', (name,))
        else:
            
            c.execute(f'SELECT * FROM themes WHERE id = ?', (id,))
        theme_data: tuple[int, str, str, str, str, int] = c.fetchone()
        c.close()
        if theme_data == None: return None
        print(f"Theme data: {theme_data}")
        # Index: id = 0, themeName = 1, description = 2, data = 3, author = 4, stars = 5
        return {
            "id": theme_data[0],
            "themeName": theme_data[1],
            "description": theme_data[2],
            "data": theme_data[3],
            "author": theme_data[4],
            "stars": theme_data[5]
        }

    def change_theme_data_for_name_or_id(self, *, user: str | None = None, id: int | None = None, newData: ThemeDataReturnType):
        if (user == None and id == None):
            raise ValueError("User and ID == null. One must not be null for indexing")
        if (user != None and id != None):
            raise ValueError("One must be none. Only one is needed for indexing")
        c = self.themes_database_db.cursor()
        if id:
            c.execute('''
            UPDATE themes
            SET themeName = ?, description = ?, data = ?, author = ?, stars = ?
            WHERE id = ?
            ''', (newData["themeName"], newData["description"], newData["data"], newData["author"], newData["stars"], id))
        else:
            c.execute('''
            UPDATE themes
            SET themeName = ?, description = ?, data = ?, author = ?, stars = ?
            WHERE themeName = ?
            ''', (newData["themeName"], newData["description"], newData["data"], newData["author"], newData["stars"], newData["themeName"]))
        c.close()
        self.themes_database_db.commit()

    
    def register_new_row_authentication_data_for_user(self, username: str, favorites: str, ownedThemes: str, password: str, publicKey: str, privateKey: str, iv:str) -> None:
        """
        Registers a new user to the database. Note: password represents hashed password, not raw password.
        """
        c = self.user_data_database_db.cursor()
        c.execute('''
        INSERT INTO users (username, favorites, ownedThemes, password, publicKey, privateKey, iv)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, favorites, ownedThemes, password, publicKey, privateKey, iv))
        c.close()
        self.user_data_database_db.commit()

    def register_new_row_theme_data_for_name(self, name: str, description: str, data: str, author: str, stars: int) -> int:
        """
        Registers a new theme to the database. Note: password represents hashed password, not raw password.
        """
        c = self.themes_database_db.cursor()
        c.execute('''
        INSERT INTO themes (themeName, description, data, author, stars)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, description, data, author, stars))
        last_row = c.lastrowid
        c.close()
        self.themes_database_db.commit()
        return last_row or -1
    def delete_theme_data_by_name_or_id(self, *, name: str|None = None, id: str|None = None):
        if (name == None and id == None):
            raise ValueError("Name and ID == null. One must not be null for indexing")
        if (name != None and id != None):
            raise ValueError("One must be none. Only one is needed for indexing")
        c = self.themes_database_db.cursor()
        if id:
            c.execute('''DELETE FROM themes
                                        WHERE id = ?;''', (id,))
        elif name != None:
            c.execute('''DELETE FROM themes
                                WHERE themeName = ?;''', (name,))
        c.close()
        self.themes_database_db.commit()