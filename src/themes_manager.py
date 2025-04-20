from src.db_provider import DatabaseProvider
from src.auth_provider import AuthProvider
from src.types import *

import traceback
import json
from pydantic import BaseModel


# Validation types
class ThemeData_FontsDictType(BaseModel):
    fontFamily: str
    imports: str

class ThemeData_DataFieldDictType(BaseModel):
    varColors: dict[str, str]
    classColors: dict[str, str]
    fonts: ThemeData_FontsDictType
    otherSettings: dict[str, str]
    twemojiSupport: bool

class ThemeDataDict(BaseModel):
    data: ThemeData_DataFieldDictType
    name: str
    data_version: int


def is_decodable_json(data: str):
    try:
        return json.loads(data)
    except: return None
def is_valid_theme(decoded_json: TDThemeDataDict):
    try:ThemeDataDict(**decoded_json); return True
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        print("Decoded JSON:", decoded_json)
        return False

class ThemesManager:

    def __init__(self, db_provider: DatabaseProvider):
        self.db_provider = db_provider
        
    def publishTheme(self, themeName: str, themeDescription: str, themeData: str, tokenData: AuthenticationToken) -> AuthProviderResultDict:
        try:
            decoded_data = is_decodable_json(themeData)
            if decoded_data == None:
                return {
                    "success": False,
                    "message": "Theme data invalid: not readable JSON",
                    "httpStatus": 400
                }
            if is_valid_theme(decoded_data) == False:
                return {
                    "success": False,
                    "message": "Theme data is not valid",
                    "httpStatus": 400
                }


            if len(themeName) < 4 or len(themeDescription) < 12 or len(themeData) < 154:
                return {
                    "success": False,
                    "message": "Theme name (>= 4 characters), theme description (>= 12 characters), or theme data (>= 154 characters) too short",
                    "httpStatus": 400
                }

            if len(themeName) > 255:
                return {
                    'success': False,
                    "message": "Title cannot exceed 255 characters",
                    "httpStatus": 400
                }
            if len(themeDescription) > 2047:
                return {
                    "success": False,
                    "message": "Description cannot exceed 2047 characters",
                    "httpStatus": 400
                }
            if self.db_provider.read_theme_data_for_name_or_id(name=themeName) != None:
                return {
                    "success": False,
                    "message": "Theme name already in use!",
                    "httpStatus": 400
                }

            user_data = self.db_provider.read_authentication_data_for_user_or_id(id=tokenData.get("id"))
            if user_data == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }

            decodedOwnedThemes: list[int] = json.loads(user_data["ownedThemes"])
            

            lastrow = self.db_provider.register_new_row_theme_data_for_name(themeName, themeDescription, themeData, tokenData.get("username"), 0)
            decodedOwnedThemes.append(lastrow)

            self.db_provider.change_authentication_data_for_name_or_id(id=tokenData.get("id"), newData={
                "id": user_data["id"],
                "favorites": user_data["favorites"],
                "ownedThemes": json.dumps(decodedOwnedThemes),
                "password": user_data["password"],
                "username": user_data["username"],
                "publicKey": user_data["publicKey"],
                "privateKey": user_data["privateKey"],
                "iv": user_data["iv"]
            })

            return {
                "success": True,
                "message": "OK",
                "httpStatus": 200
            }
        except Exception as e:
            print("Failed", traceback.format_exc())
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
        
    def deleteTheme(self, themeName: str, tokenData: AuthenticationToken) -> AuthProviderResultDict:
        try:
            themeData: ThemeDataReturnType = self.db_provider.read_theme_data_for_name_or_id(name=themeName)

            if themeData == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }
            userData: AuthenticationDataReturnType = self.db_provider.read_authentication_data_for_user_or_id(id=tokenData.get("id"))
            if (userData == None):
                return {
                    "success": False,
                    "message": "Username not found",
                    "httpStatus": 404
                }
            
            decodedOwnedThemes: list[int] = json.loads(userData["ownedThemes"])
            decodedOwnedThemes.index(themeData["id"])

            self.db_provider.delete_theme_data_by_name_or_id(name=themeName)

            
            decodedOwnedThemes.remove(themeData["id"])
            self.db_provider.change_authentication_data_for_name_or_id(id=userData["id"], newData={
                "id": userData["id"],
                "favorites": userData["favorites"],
                "ownedThemes": json.dumps(decodedOwnedThemes),
                "password": userData["password"],
                "username": userData["username"],
                "publicKey": userData["publicKey"],
                "privateKey": userData["privateKey"],
                "iv": userData["iv"]
            })

            return {
                "success": True,
                "message": "OK",
                "httpStatus": 200
            }
        except Exception as e:
            print("Failed: ", e)
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
    
    def getOwned(self, tokenData: AuthenticationToken) -> AuthProviderResultDict:
        try:
            print(f"User: {tokenData["username"]}")
            user_data = self.db_provider.read_authentication_data_for_user_or_id(id=tokenData.get("id"))
            if user_data == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }

            user_owned = json.loads(user_data["ownedThemes"])
            if user_owned != None:
                owned = []
                for i in user_owned:
                    theme_data = self.db_provider.read_theme_data_for_name_or_id(id=i)
                    if theme_data == None:
                        print(f"Error: failed to get theme data: ID does not exist: {i}")
                        continue
                    
                    owned.append(theme_data["themeName"])

                return {
                    "success": True,
                    "message": "OK",
                    "data": owned,
                    "httpStatus": 200
                }
            else: return {
                "success": False,
                "message": "User not found",
                "httpStatus": 404
            }
        except Exception as e:
            print("Failed: ", e)
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
    def getThemeInfo(self, themeName: str) -> AuthProviderResultDict:
        try:
            theme_data = self.db_provider.read_theme_data_for_name_or_id(name=themeName)

            if theme_data == None:
                return {
                    "success": False,
                    "message": "Theme not found",
                    "httpStatus": 404
                }
            
            new_json = {
                "name": theme_data["themeName"],
                "desc": theme_data["description"],
                "data": theme_data["data"],
                "author": theme_data["author"],
                "stars": theme_data["stars"]
            }

            return {
                "success": True,
                "message": "OK",
                "data": new_json,
                "httpStatus": 200
            }
        except Exception as e:
            print("Failed: ", e)
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
    def getThemes(self, search_term:str | None) -> AuthProviderResultDict:
        try:
            search_term = search_term or ''
            print(search_term)
            c = self.db_provider.themes_database_db.cursor()
            c.execute('''
                SELECT * FROM themes
                WHERE themeName LIKE ?
            ''', ('%' + search_term + '%',))

            # Fetch and print the results
            rows = c.fetchall()
            c.close()
            final_data: dict[str, ThemeDataReturnType] = {}
            for row in rows:

                row_json: ThemeDataReturnType = {
                    "id": row[0],
                    "themeName": row[1],
                    "description": row[2],
                    "data": row[3],
                    "author": row[4],
                    "stars": row[5]
                }

                new_json = {
                    "name": row_json["themeName"],
                    "desc": row_json["description"],
                    "data": row_json["data"],
                    "author": row_json["author"],
                    "stars": row_json["stars"]
                }

                print(row_json)
            
                final_data[row_json["themeName"]] = new_json

            return {
                "success": True,
                "message": "OK",
                "data": final_data,
                "httpStatus": 200
            }
        except Exception as e:
            print("Failed: ", e)
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
    def starTheme(self, tokenData:AuthenticationToken, themeName: str) -> AuthProviderResultDict:
        try:
            if themeName == None:
                return jsonify(success=False, message="Theme not found"), 404
            
            userData = self.db_provider.read_authentication_data_for_user_or_id(id=tokenData.get("id"))
            themeData = self.db_provider.read_theme_data_for_name_or_id(name=themeName)
            if userData == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }

            if themeData == None:
                return {
                    "success": False,
                    "message": "Theme not found",
                    "httpStatus": 404
                }
            
            decoded_fav: list[int] = json.loads(userData["favorites"])


                
            if themeData["id"] in decoded_fav:
                self.db_provider.change_theme_data_for_name_or_id(id=themeData["id"], newData={
                    "id": themeData["id"],
                    "author": themeData["author"],
                    "data": themeData["data"],
                    "description": themeData["description"],
                    "stars": themeData["stars"] - 1,
                    "themeName": themeData["themeName"]
                })
                decoded_fav.remove(themeData["id"])
                
                self.db_provider.change_authentication_data_for_name_or_id(id=tokenData.get("id"), newData={
                    "favorites": json.dumps(decoded_fav),
                    "id": userData["favorites"],
                    "ownedThemes": userData["ownedThemes"],
                    "password": userData["password"],
                    "username": userData["username"],
                    "publicKey": userData["publicKey"],
                    "privateKey": userData["privateKey"],
                    "iv": userData["iv"]
                })

                return {
                    "success": True,
                    "message": "OK",
                    "httpStatus": 200
                }
                
            self.db_provider.change_theme_data_for_name_or_id(id=themeData["id"], newData={
                "id": themeData["id"],
                "author": themeData["author"],
                "data": themeData["data"],
                "description": themeData["description"],
                "stars": themeData["stars"] + 1,
                "themeName": themeData["themeName"]
            })
            decoded_fav.append(themeData["id"])
            
            self.db_provider.change_authentication_data_for_name_or_id(id=tokenData.get("id"), newData={
                "favorites": json.dumps(decoded_fav),
                "id": userData["favorites"],
                "ownedThemes": userData["ownedThemes"],
                "password": userData["password"],
                "username": userData["username"],
                "publicKey": userData["publicKey"],
                "privateKey": userData["privateKey"],
                "iv": userData["iv"]
            })

            return {
                "success": True,
                "message": "OK",
                "httpStatus": 200
            }
        except Exception as e:
            print("Failed: ", traceback.format_exc())
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
    def getThemeStarred(self, tokenData:AuthenticationToken, themeName:str) -> AuthProviderResultDict:
        try:
            userData = self.db_provider.read_authentication_data_for_user_or_id(id=tokenData.get("id"))
            themeData = self.db_provider.read_theme_data_for_name_or_id(name=themeName)
            if userData == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }

            if themeData == None:
                return {
                    "success": False,
                    "message": "Theme not found",
                    "httpStatus": 404
                }

            if not (themeData["id"] in json.loads(userData["favorites"])):
                return {
                    "success": True,
                    "message": "OK",
                    "data": False,
                    "httpStatus": 200
                }
            else:
                return {
                    "success": True,
                    "message": "OK",
                    "data": True,
                    "httpStatus": 200
                }
        except Exception as e:
            print("Failed: ", e)
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }