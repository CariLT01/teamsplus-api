from src.databaseHelper import Database
from src.databaseHelper import DatabaseKeyValuePair

from typing import Any, cast
from src.custom_types import *

class DatabaseProvider:

    def __init__(self, db_path: str = "databases/users.db"):
        self.db = Database(db_path)
        self.load_databases()
    def load_databases(self) -> None:
        self.db.create_table_if_not_exists("users", {
            "id": "INTEGER PRIMARY KEY",
            "username": "VARCHAR(31)",
            "favorites": "TEXT NOT NULL",
            "ownedThemes": "TEXT NOT NULL",
            "password": "VARCHAR(60)",
            "publicKey": "TEXT",
            "privateKey": "TEXT",
            "iv": "TEXT"
        })

        self.db.create_table_if_not_exists("themes", {
            "id": "INTEGER PRIMARY KEY",
            "themeName": "VARCHAR(255)",
            "description": "VARCHAR(2047)",
            "data": "TEXT NOT NULL",
            "author": "TEXT NOT NULL",
            "stars": "INT NOT NULL"
        })
                                           
                                           
                                           


    def read_user_data(self, **kwargs: Any) -> AuthenticationDataReturnType | None:
        if not kwargs:
            return None
        queryKey, queryValue = next(iter(kwargs.items()))
        return cast(AuthenticationDataReturnType, self.db.read_row_from_table("users", queryKey, queryValue, ["id", "username", "favorites", "ownedThemes", "password", "publicKey", "privateKey", "iv"]))

    def change_user_data(self, values: dict[str, Any], **kwargs: Any) -> None:
        if not kwargs: return None
        qk, qv = next(iter(kwargs.items()))
        return self.db.change_row_in_table("users", values, qk, qv)
    
    def delete_user_data(self, **kwargs: Any) -> None:
        if not kwargs: return None
        qk, qv = next(iter(kwargs.items()))
        self.db.delete_row("users", qk, qv)
    
    def add_user(self, values: dict[str, Any]) -> int|None:
        return self.db.add_new_row("users", values)   


    def read_theme_data(self, **kwargs: Any) -> ThemeDataReturnType | None:
        if not kwargs:
            return None
        queryKey, queryValue = next(iter(kwargs.items()))
        return cast(ThemeDataReturnType, self.db.read_row_from_table("themes", queryKey, queryValue, ["id", "themeName", "description", "data", "author", "stars"]))

    def change_theme_data(self, values: dict[str, Any], **kwargs: Any) -> None:
        if not kwargs: return None
        qk, qv = next(iter(kwargs.items()))
        return self.db.change_row_in_table("themes", values, qk, qv)
    
    def delete_theme_data(self, **kwargs: Any) -> None:
        if not kwargs: return None
        qk, qv = next(iter(kwargs.items()))
        self.db.delete_row("themes", qk, qv)
    
    def add_theme(self, values: dict[str, Any]) -> int|None:
        return self.db.add_new_row("themes", values)   