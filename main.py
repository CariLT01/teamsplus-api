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
from src.game_of_life.game_of_life import GameOfLife
from src.httpServer import Flask_HTTPServer
import src.versions as versions

import src.static_pages as static_pages

httpServer = Flask_HTTPServer()





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








class MainApp:

    def __init__(self) -> None:
        self.httpServer = Flask_HTTPServer()
        self.db_provider = DatabaseProvider()
        self.authProvider = AuthProvider(self.db_provider)
        self.themeManager = ThemesManager(self.db_provider)
        self.encryptionProvider = EncryptionProvider(self.db_provider)
        self.gameOfLifeProvider = GameOfLife(self.authProvider)
    
    def initialize(self) -> None:
        self.add_routes()

    def add_routes(self) -> None:

        # Static pages

        self.httpServer.add_route("/", static_pages.home)
        self.httpServer.add_route("/dashboard", static_pages.dashboard_page)
        self.httpServer.add_route("/login", static_pages.login_page)
        self.httpServer.add_route("/register", static_pages.register_page)
        self.httpServer.add_route("/game_of_life", static_pages.game_of_life_page)

        # Authentication routes
        self.httpServer.add_route("/api/v1/auth/login", self.authProvider.auth_route, methods=["POST"])
        self.httpServer.add_route("/api/v1/auth/register", self.authProvider.register_route, methods=["POST"])

        # TeamsPlus download routes
        self.httpServer.add_route("/api/v1/versions/get", versions.get_versions_route, methods=["GET"])
        self.httpServer.add_route("/api/v1/versions/get_file", versions.get_file_route, methods=['GET'])
        self.httpServer.add_route("/api/v1/versions/download", versions.get_link_from_version_route, methods=["GET"])

        # Themes API routes
        self.httpServer.add_route("/api/v1/themes/publish", lambda: self.themeManager.publish_theme_route(self.authProvider), methods=['POST'])
        self.httpServer.add_route("/api/v1/themes/delete", lambda: self.themeManager.delete_theme_route(self.authProvider), methods=["POST"])
        self.httpServer.add_route("/api/v1/themes/get_owned", lambda: self.themeManager.get_owned_route(self.authProvider), methods=["GET"])
        self.httpServer.add_route("/api/v1/themes/get_info", self.themeManager.get_theme_info_route, methods=["GET"])
        self.httpServer.add_route("/api/v1/themes/get", self.themeManager.get_themes_route, methods=["GET"])
        self.httpServer.add_route("/api/v1/themes/star", lambda: self.themeManager.star_theme_route(self.authProvider), methods=["POST"])
        self.httpServer.add_route("/api/v1/themes/wait_did_i_star_this", lambda: self.themeManager.get_theme_starred_route(self.authProvider), methods=["GET"])

        # Encryption API routes
        self.httpServer.add_route("/api/v1/encryption/encrypt", lambda: self.encryptionProvider.encrypt_route(self.authProvider), methods=['POST'])
        self.httpServer.add_route("/api/v1/encryption/decrypt", lambda: self.encryptionProvider.decrypt_route(self.authProvider), methods=["POST"])
        self.httpServer.add_route("/api/v1/auth/search", self.authProvider.search_users_route, methods=["GET"])

        # GOL API routes
        self.httpServer.add_route("/api/v1/game_of_life/get_event", self.gameOfLifeProvider.game_of_life_get_event_route, methods=["GET"])
        self.httpServer.add_route("/api/v1/game_of_life/option_select_post", lambda: self.gameOfLifeProvider.game_of_life_option_select_post_route(self.authProvider), methods=["POST"])

    def run(self) -> None:

        self.httpServer.run()


if __name__ == '__main__':

    app = MainApp()
    app.initialize()
    app.run()