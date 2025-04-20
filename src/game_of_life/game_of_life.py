from flask import request
from src.auth_provider import AuthProvider

from src.custom_types import *

import random

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