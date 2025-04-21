from flask import request, Response, jsonify
from src.auth_provider import AuthProvider

from src.custom_types import *

import random
import traceback

# Utility functions

def generate_request_data(success: bool, message: str, data: GOL_HTTP_Data | None, httpStatus: int) -> GameOfLife_HTTPGetEventReturnType:
    return {
        'success': success,
        'message': message,
        'data': data,
        'httpStatus': httpStatus
    }   

class GameOfLife:

    def __init__(self, authProvider: AuthProvider):
        self.authProvider = authProvider

    def serve_event_get_request(self) -> GameOfLife_HTTPGetEventReturnType:
        """
        Function that runs when /api/v1/game_of_life/get_event is called.
        """
        # Inside request context

        tokenPayload = self.authProvider.check_token(request) # Fetch JWT token
        if tokenPayload == None:
            return generate_request_data(False, "Invalid token", None, 401)
        
        username = tokenPayload['username'] # Example

        return generate_request_data(True, # Temporary return statement
                                     "OK", {
                                         "content": "<p>Hello. This is temporary.</p>",
                                         "eventId": random.randint(0, 999999), # Event ID remains random
                                         "options": ["Option 1", "Option 2", "Option 3"] # As many options as you want
                                     }, 200)

    def serve_event_post_request(self) -> GameOfLife_HTTPGetEventReturnType:
        """
        Function that runs when /api/v1/game_of_life/post_event is called.
        """

        # Inside request context

        tokenPayload = self.authProvider.check_token(request)
        if tokenPayload == None:
            return generate_request_data(False, "Invalid token", None, 401)
        
        username = tokenPayload['username'] # Example

        return generate_request_data(True, "Not implemented", None, 200) # Temporary HTTP response
        
    def game_of_life_get_event_route(self)->tuple[Response, int]:
        try:
            resp = self.serve_event_get_request()
            return jsonify(resp), resp["httpStatus"]
        except Exception as e:
            print("Failed: ", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500
    
    def game_of_life_option_select_post_route(self, authProvider: AuthProvider)->tuple[Response, int]:
        try:
            tokenData = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
            
            resp = self.serve_event_post_request()
            return jsonify(resp), resp["httpStatus"]

        except Exception as e:
            print("Failed: ", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500