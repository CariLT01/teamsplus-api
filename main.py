import json, traceback
from typing import TypedDict, NoReturn
from pydantic import BaseModel
import platform

from flask import Flask, request, jsonify, render_template, make_response, Response
from flask_cors import CORS

from typing import Any, cast

from src.auth_provider import AuthProvider
from src.db_provider import DatabaseProvider
from src.themes_manager import ThemesManager
from src.custom_types import *
from src.encryption_provider import EncryptionProvider
from src.config import *



app = Flask(__name__)
db_provider = DatabaseProvider()
authProvider = AuthProvider(db_provider)
themeManager = ThemesManager(db_provider)
encryptionProvider = EncryptionProvider(db_provider)
CORS(app, origins=["https://teams.microsoft.com"]) # Fix CORS issue during development

# Compare types

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


class VersionsDict(TypedDict):
    versions: dict[str, str]
    latest: str



def read_versions_file()->VersionsDict:
    with open(f"{ABSOLUTE_PATH}data/versions.json", "r") as f: return cast(VersionsDict, json.loads(f.read()))


    

@app.route("/")
def home()->str:
    return render_template("home/index.html")
@app.route("/login")
def login_page()->str:
    return render_template("loginPage/index.html")
@app.route("/dashboard")
def dashboard_page()->str:
    return render_template("dashboard/index.html")
@app.route("/register")
def register_page()->str:
    return render_template("registerPage/index.html")



@app.route("/api/v1/auth/login", methods=['POST'])
def auth()->tuple[Response, int]:
    try:
        print("AUH AUTH AUTH AUTH", flush=True)
        print("*")
        data: Any = request.get_json()
        username = data.get('username')
        password = data.get('password')
        transfer = data.get('transfer')

        if (username == None or password == None):
            return jsonify(success=False, message="Bad request"), 400

        # Get the username in the JSON file
        
        out, tok = authProvider.auth(username, password, transfer or False)
        if tok:
            resp = make_response(jsonify(out))
            resp.set_cookie("jwt", tok, max_age=TOKEN_EXPIRY_INT, httponly=True, secure=False)
            return resp, out['httpStatus']
        return jsonify(out), out['httpStatus']
    except Exception as e:
        print("Failed: ", e)
        return jsonify(success=False, message="Unknown error", errorId="UKW_ERR"), 500

@app.route("/api/v1/versions/get", methods=['GET'])
def get_versions()->tuple[Response, int]:
    try:
        versions_file = read_versions_file()

        versions = versions_file["versions"]

        versions_list = []
        for i in versions:
            versions_list.append(i)
        
        latest = versions_file["latest"]

        return jsonify(success=True, message="OK", data={
            "latest": latest,
            "versions": versions_list
        }), 200
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500

@app.route("/api/v1/versions/get_file", methods=['GET'])
def get_file()->tuple[Response, int]:
    try:
        query_version = request.args.get("version")
        if query_version == None:
            return jsonify(success=False, message="No version specified"), 400
        
        versions_file = read_versions_file()
        versions: dict[str, str] = versions_file["versions"]
        
        version_info = versions.get(query_version)
        if query_version == 'latest':
            version_info = versions.get(versions_file["latest"])
        if version_info == None:
            return jsonify(success=False, message="Version not found"), 404
        
        return jsonify(success=True, message="OK", data=f"{version_info}.zip"), 200
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500        

@app.route("/api/v1/versions/download", methods=['GET'])
def get_link_from_version()->tuple[Response, int]:
    try:
        query_file = request.args.get("file")
        if query_file == None:
            return jsonify(success=False, message="No file specified"), 400

        return jsonify(success=True, message="OK", data=f"{DOWNLOAD_URL}{query_file}"), 200

    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500        



@app.route("/api/v1/auth/register", methods=['POST'])
def register()->tuple[Response, int]:
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        captcha = data.get('captcha')

        if username == None or password == None or captcha == None:
            return jsonify(success=False, message="Bad request"), 400

        auth = authProvider.register(username, password, captcha)
        

        return jsonify(auth), auth['httpStatus']
    except Exception as e:
        print("it fucking Failed: ", e)
        return jsonify(success=False, message="Unknown error", errorId="UKW_ERR"), 500



@app.route("/api/v1/themes/publish", methods=['POST'])
def publish_theme()->tuple[Response, int]:
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
        
        result = themeManager.publishTheme(themeName, themeDescription, themeData, tokenData)

        return jsonify(result), result['httpStatus']
        
    except Exception as e:
        print("Failed", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500
@app.route("/api/v1/themes/delete", methods=['POST'])
def delete_theme()->tuple[Response, int]:
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
        
        result = themeManager.deleteTheme(themeName, tokenData)
        return jsonify(result), result["httpStatus"]

    except Exception as e:
        print("Failed", e)
        return jsonify(success=False, message="Internal server error"), 500
    


@app.route("/api/v1/themes/get_owned", methods=['GET'])
def get_owned()->tuple[Response, int]:
        try:
            tokenData: AuthenticationToken | None = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
            print(tokenData.get("id"))
            
            result = themeManager.getOwned(tokenData)
            return jsonify(result), result['httpStatus']
        except Exception as e:
            print("Failed", e)
            return jsonify(success=False, message="Internal server error"), 500
@app.route("/api/v1/themes/get_info", methods=['GET'])
def get_theme_info()->tuple[Response, int]:
    try:
        themeName = request.args.get("theme")
        if themeName == None:
            return jsonify(success=False, message="Theme name not provided"), 401
        out = themeManager.getThemeInfo(themeName)

        return jsonify(out), out["httpStatus"]
    except Exception as e:
        print("Failed", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500

@app.route("/api/v1/themes/get", methods=['GET'])
def get_themes()->tuple[Response, int]:
    try:
        search_term = request.args.get('search')
        
        out = themeManager.getThemes(search_term)
        return jsonify(out), out["httpStatus"] 
        
    except Exception as e:
        print("Failed", e)
        return jsonify(success=False, message="Failed to fetch themes", errorId="THEMES_FETCH_FAILED"), 500
@app.route("/api/v1/themes/star", methods=['POST'])
def star_theme()->tuple[Response, int]:
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
        out = themeManager.starTheme(tokenData, themeName)
        return jsonify(out), out["httpStatus"]


        
    except Exception as e:
        print("Failed", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500
@app.route("/api/v1/themes/wait_did_i_star_this", methods=['GET'])
def get_theme_starred()->tuple[Response, int]:
    try:
        tokenData = authProvider.check_token(request)
        if tokenData == None:
            return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
        if tokenData.get("username") == None:
            return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401

        themeName = request.args.get("name")
        if themeName == None:
            return jsonify(success=False, message="Theme name not provided"), 400
        out = themeManager.getThemeStarred(tokenData, themeName)
        return jsonify(out), out["httpStatus"]
        
    except Exception as e:
        print("Failed", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500

@app.route("/api/v1/encryption/encrypt", methods=['POST'])
def encrypt()->tuple[Response, int]:

    try:
        tokenData = authProvider.check_token(request)
        if tokenData == None:
            return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
        if tokenData.get("username") == None:
            return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
        requestData = request.get_json()

        dest_user_id = requestData.get("destination")
        body = requestData.get("body")
        password = requestData.get("pwd")

        if (dest_user_id == None or body == None or password == None):
            return jsonify(success=False, message="Bad request"), 400

        output = encryptionProvider.encrypt(dest_user_id, body, password, tokenData)

        return jsonify(output), output["httpStatus"]


    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500

@app.route("/api/v1/encryption/decrypt", methods=['POST'])
def decrypt()->tuple[Response, int]:

    try:
        tokenData = authProvider.check_token(request)
        if tokenData == None:
            return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
        if tokenData.get("username") == None:
            return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
        requestData = request.get_json()

        
        body = requestData.get("body")
        password = requestData.get("pwd")
        signature = requestData.get("signature")
        iv = requestData.get("iv")
        key = requestData.get("key")
        author = requestData.get("author")

        if (body == None or password == None or signature == None or iv == None or key == None or author == None):
            return jsonify(success=False, message="Bad request"), 400

        output = encryptionProvider.decrypt(signature, body, iv, key, tokenData, password, author)

        return jsonify(output), output["httpStatus"]


    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500

@app.route("/api/v1/auth/search", methods=["GET"])
def search_users()->tuple[Response, int]:
    try:
        search_term = request.args.get("search")
        if search_term == None:
            return jsonify(success=False, message="No search term provided"), 400

        out = authProvider.search_users(search_term)
        return jsonify(out), out["httpStatus"]
    except Exception as e:
        print("Failed: ", traceback.format_exc())
        return jsonify(success=False, message="Internal server error"), 500


if platform.system() == 'Windows':
    app.run()