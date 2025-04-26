from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS

import platform
import random
import os



from typing import Literal
from typing import Callable
from typing import Union
from typing import Any

from src.config import *

ViewReturnType = Union[
    Response, str, bytes, list[Any], dict[str, Any],
    tuple[Any, int], tuple[Any, int, dict[str, Any]]
]

class Flask_HTTPServer:
    def __init__(self, cors: bool = True, origins: list[str]=["https://teams.microsoft.com"]) -> None:
        
        templates_path = os.path.abspath(f'{ABSOLUTE_PATH}templates')
        static_path = os.path.abspath(f'{ABSOLUTE_PATH}static')
        print(templates_path, static_path)
        self.app = Flask(__name__, template_folder=templates_path, static_folder=static_path)

                # Get the absolute path of the templates folder


        if cors == True:
            CORS(self.app, origins=origins)

    def add_route(self, route: str, view_func: Callable[..., ViewReturnType], methods: list[Literal['GET', 'POST', 'PUT', 'OPTIONS', 'PATCH', 'DELETE', 'HEAD', 'TRACE', 'CONNECT']]=['GET']) -> None:

        self.app.add_url_rule(route, view_func=view_func, methods=methods, endpoint=str(random.randint(0, 9999999999999)))
    
    def run(self, port: int = 5000) -> None:
        if platform.system() == 'Windows': # Prevent running app.run in production
            self.app.run(port=port)