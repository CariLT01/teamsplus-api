from src.db_provider import DatabaseProvider
from src.auth_provider import AuthProvider
from src.custom_types import *

import traceback
import json
from pydantic import BaseModel

from typing import Any, cast

from flask import request, jsonify, Response


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


def is_decodable_json(data: str)-> Any | None:
    try:
        return json.loads(data)
    except: return None
def is_valid_theme(decoded_json: Any) -> bool:
    try:ThemeDataDict(**decoded_json); return True
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        print("Decoded JSON:", decoded_json)
        return False

class ThemesManager:

    def __init__(self, db_provider: DatabaseProvider):
        self.db_provider = db_provider
        
    def publishTheme(self, themeName: str, themeDescription: str, themeData: str, tokenData: AuthenticationToken) -> HTTPRequestResponseDict:
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
            if self.db_provider.read_theme_data(themeName=themeName) != None:
                return {
                    "success": False,
                    "message": "Theme name already in use!",
                    "httpStatus": 400
                }

            user_data = self.db_provider.read_user_data(id=tokenData.get("id"))
            if user_data == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }

            decodedOwnedThemes: list[int] = json.loads(user_data["ownedThemes"])
            

            #lastrow = self.db_provider.add_theme(themeName, themeDescription, themeData, tokenData["username"], 0)
            lastrow = self.db_provider.add_theme({
                "themeName": themeName,
                "description": themeDescription,
                "data": themeData,
                "author": tokenData["username"],
                "stars": 0
            })
            decodedOwnedThemes.append(cast(int, lastrow))

            self.db_provider.change_user_data({
                "id": user_data["id"],
                "favorites": user_data["favorites"],
                "ownedThemes": json.dumps(decodedOwnedThemes),
                "password": user_data["password"],
                "username": user_data["username"],
                "publicKey": user_data["publicKey"],
                "privateKey": user_data["privateKey"],
                "iv": user_data["iv"]
            }, id=tokenData.get("id"))

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
        
    def deleteTheme(self, themeName: str, tokenData: AuthenticationToken) -> HTTPRequestResponseDict:
        try:
            themeData: ThemeDataReturnType | None = self.db_provider.read_theme_data(themeName=themeName)

            if themeData == None:
                return {
                    "success": False,
                    "message": "User not found",
                    "httpStatus": 404
                }
            userData: AuthenticationDataReturnType | None = self.db_provider.read_user_data(id=tokenData.get("id"))
            if (userData == None):
                return {
                    "success": False,
                    "message": "Username not found",
                    "httpStatus": 404
                }
            
            decodedOwnedThemes: list[int] = json.loads(userData["ownedThemes"])
            decodedOwnedThemes.index(themeData["id"])

            self.db_provider.delete_theme_data(themeName=themeName)

            
            decodedOwnedThemes.remove(themeData["id"])
            self.db_provider.change_user_data({
                "id": userData["id"],
                "favorites": userData["favorites"],
                "ownedThemes": json.dumps(decodedOwnedThemes),
                "password": userData["password"],
                "username": userData["username"],
                "publicKey": userData["publicKey"],
                "privateKey": userData["privateKey"],
                "iv": userData["iv"]
            }, id=userData["id"])

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
    
    def getOwned(self, tokenData: AuthenticationToken) -> HTTPRequestResponseDict:
        try:
            print(f"User: {tokenData["username"]}")
            user_data = self.db_provider.read_user_data(id=tokenData.get("id"))
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
                    theme_data = self.db_provider.read_theme_data(id=i)
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
    def getThemeInfo(self, themeName: str) -> HTTPRequestResponseDict:
        try:
            theme_data = self.db_provider.read_theme_data(themeName=themeName)

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
    def getThemes(self, search_term:str | None) -> HTTPRequestResponseDict:
        try:
            search_term = search_term or ''
            print(search_term)
            c = self.db_provider.db.database.cursor()
            c.execute('''
                SELECT * FROM themes
                WHERE themeName LIKE ?
            ''', ('%' + search_term + '%',))

            # Fetch and print the results
            rows = c.fetchall()
            c.close()
            final_data: dict[str, ThemeSearchFinalListEntryDict] = {}
            for row in rows:

                row_json: ThemeDataReturnType = {
                    "id": row[0],
                    "themeName": row[1],
                    "description": row[2],
                    "data": row[3],
                    "author": row[4],
                    "stars": row[5]
                }

                new_json: ThemeSearchFinalListEntryDict = {
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
    def starTheme(self, tokenData:AuthenticationToken, themeName: str) -> HTTPRequestResponseDict:
        try:
            if themeName == None:
                return {
                    "success": False,
                    "message": "Theme not found",
                    "httpStatus": 404
                }
            
            userData = self.db_provider.read_user_data(id=tokenData.get("id"))
            themeData = self.db_provider.read_theme_data(themeName=themeName)
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
                self.db_provider.change_theme_data({
                    "id": themeData["id"],
                    "author": themeData["author"],
                    "data": themeData["data"],
                    "description": themeData["description"],
                    "stars": themeData["stars"] - 1,
                    "themeName": themeData["themeName"]
                }, id=themeData["id"])
                decoded_fav.remove(themeData["id"])
                
                self.db_provider.change_user_data({
                    "favorites": json.dumps(decoded_fav),
                    "id": userData["id"],
                    "ownedThemes": userData["ownedThemes"],
                    "password": userData["password"],
                    "username": userData["username"],
                    "publicKey": userData["publicKey"],
                    "privateKey": userData["privateKey"],
                    "iv": userData["iv"]
                }, id=tokenData.get("id"))

                return {
                    "success": True,
                    "message": "OK",
                    "httpStatus": 200
                }
                
            self.db_provider.change_theme_data({
                "id": themeData["id"],
                "author": themeData["author"],
                "data": themeData["data"],
                "description": themeData["description"],
                "stars": themeData["stars"] + 1,
                "themeName": themeData["themeName"]
            }, id=themeData["id"])
            decoded_fav.append(themeData["id"])
            
            self.db_provider.change_user_data({
                "favorites": json.dumps(decoded_fav),
                "id": userData["id"],
                "ownedThemes": userData["ownedThemes"],
                "password": userData["password"],
                "username": userData["username"],
                "publicKey": userData["publicKey"],
                "privateKey": userData["privateKey"],
                "iv": userData["iv"]
            }, id=tokenData.get("id"))

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
    def getThemeStarred(self, tokenData:AuthenticationToken, themeName:str) -> HTTPRequestResponseDict:
        try:
            userData = self.db_provider.read_user_data(id=tokenData.get("id"))
            themeData = self.db_provider.read_theme_data(themeName=themeName)
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
    
    def publish_theme_route(self, authProvider: AuthProvider)->tuple[Response, int]:
        try:
            tokenData: AuthenticationToken | None = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
            data = request.get_json()
            themeName = data.get("themeName")
            themeDescription = data.get("themeDescription")
            themeData = data.get("themeData")

            if themeName == None or themeDescription == None or themeData == None:
                return jsonify(success=False, message="Bad request"), 400
            
            result = self.publishTheme(themeName, themeDescription, themeData, tokenData)

            return jsonify(result), result['httpStatus']
            
        except Exception as e:
            print("Failed", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500
    
    def delete_theme_route(self, authProvider: AuthProvider)->tuple[Response, int]:
        try:
            tokenData: AuthenticationToken | None = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401

            data = request.get_json()
            themeName = data.get("name")
            if themeName == None:
                return jsonify(success=False, message="No theme name"), 400
            
            result = self.deleteTheme(themeName, tokenData)
            return jsonify(result), result["httpStatus"]

        except Exception as e:
            print("Failed", e)
            return jsonify(success=False, message="Internal server error"), 500

    def get_owned_route(self, authProvider: AuthProvider)->tuple[Response, int]:
            try:
                tokenData: AuthenticationToken | None = authProvider.check_token(request)
                if tokenData == None:
                    return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
                if tokenData.get("username") == None:
                    return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
                print(tokenData.get("id"))
                
                result = self.getOwned(tokenData)
                return jsonify(result), result['httpStatus']
            except Exception as e:
                print("Failed", e)
                return jsonify(success=False, message="Internal server error"), 500

    def get_theme_info_route(self)->tuple[Response, int]:
        try:
            themeName = request.args.get("theme")
            if themeName == None:
                return jsonify(success=False, message="Theme name not provided"), 401
            out = self.getThemeInfo(themeName)

            return jsonify(out), out["httpStatus"]
        except Exception as e:
            print("Failed", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500

    def get_themes_route(self)->tuple[Response, int]:
        try:
            search_term = request.args.get('search')
            
            out = self.getThemes(search_term)
            return jsonify(out), out["httpStatus"] 
            
        except Exception as e:
            print("Failed", e)
            return jsonify(success=False, message="Failed to fetch themes", errorId="THEMES_FETCH_FAILED"), 500
    def star_theme_route(self, authProvider: AuthProvider)->tuple[Response, int]:
        try:
            tokenData: AuthenticationToken | None = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401

            requestData = request.get_json()
            themeName = requestData.get("name")
            
            if themeName == None:
                return jsonify(success=False, message="No theme name specified"), 400
            out = self.starTheme(tokenData, themeName)
            return jsonify(out), out["httpStatus"]


            
        except Exception as e:
            print("Failed", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500

    def get_theme_starred_route(self, authProvider: AuthProvider)->tuple[Response, int]:
        try:
            tokenData = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401

            themeName = request.args.get("name")
            if themeName == None:
                return jsonify(success=False, message="Theme name not provided"), 400
            out = self.getThemeStarred(tokenData, themeName)
            return jsonify(out), out["httpStatus"]
            
        except Exception as e:
            print("Failed", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500