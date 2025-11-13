
from flask import Response, jsonify, request
from src.databaseHelper import Database
import random
import jwt
import secrets
from datetime import datetime, timedelta
from src.site_secrets import *
from src.config import ABSOLUTE_PATH
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.auth_provider import AuthProvider


class GamblingProvider:
    
    def __init__(self):
        


        self.gambling_db = Database(f"{ABSOLUTE_PATH}databases/gambling.db")
        
        self.gambling_db.create_table_if_not_exists("tokens", {
            "id": "INTEGER PRIMARY KEY",
            "valid": "INTEGER"
        })
        
        self.gambling_user_last_request: dict[int, float] = {}
        
    def does_token_id_exist(self, id: int):
        cursor = self.gambling_db.execute_command_and_return_cursor("SELECT * FROM tokens WHERE id = ?", (id,))
        return cursor.fetchone() is not None
    
    def find_token_id(self):
        
        random_id = secrets.randbits(32)
        count = 0
        while count < 100:
            
            if self.does_token_id_exist(random_id) == False:
                return random_id
            random_id = secrets.randbits(32)
            count += 1
        return None
    
    def generate_win_token(self, userId: int, reward: int):
        
        random_id = self.find_token_id()
        if random_id == None: raise RuntimeError("Could not find a valid token ID within reasonable time")
        
        payload = {
            "userId": userId,
            "tokenId": random_id,
            "reward": reward,
            "exp": datetime.now() + timedelta(days=1)
        }
        
        token = jwt.encode(payload, JWT_GAMBLING_REWARD_SECRET, algorithm="HS256")
        
        self.gambling_db.add_new_row("tokens", {
            "id": random_id,
            "valid": 1
        })
        
        return token
    
    def generate_returned_data(self, digits: list[tuple[int, int]], won: bool, isTricked: bool, authProvider: "AuthProvider") -> tuple[Response, int]:
        
        tokenData = authProvider.check_token(request)
        if tokenData == None:
            data = {
                "digits": digits,
                "winToken": "",
                "isTricked": isTricked,
                "loggedIn": False
            }
            
            return jsonify(success=True, data=data, message="OK"), 200
        else:
            
            token = ""
            if won:
                token = self.generate_win_token(tokenData.get("id"), 2)
                
            data = {
                "digits": digits,
                "winToken": token,
                "isTricked": isTricked,
                "loggedIn": True
            }
            
            return jsonify(success=True, data=data, message="OK"), 200
        
    def check_timeout(self, authProvider: "AuthProvider"):
        
        tokenData = authProvider.check_token(request)
        if not tokenData: return False
        
        userId = tokenData.get("id")
        if userId not in self.gambling_user_last_request:
            self.gambling_user_last_request[userId] = datetime.now().timestamp()
            return False
        
        last_request_time = self.gambling_user_last_request[userId]
        current_time = datetime.now().timestamp()
        
        if current_time - last_request_time < 20:
            return True
        
        self.gambling_user_last_request[userId] = current_time
        return False


    
    def slot_machine_get_next_route(self, authProvider: "AuthProvider") -> tuple[Response, int]: 
        
        if self.check_timeout(authProvider):
            return jsonify(success=False, message="Too many requests"), 429
        
        # return self.generate_returned_data([(7, 0), (7, 1), (7, 2)], True, False, authProvider) # Test;
        
        try:
            random_or_trick_score = random.uniform(0.0, 1.0)
            
            if random_or_trick_score > 0.5:
                # Should trick
                
                trick_win_score = random.uniform(0.0, 1.0)
                if trick_win_score > 0.3:
                
                    target_digit = random.randint(0, 9)
                    
                    digits = [(target_digit, 0), (target_digit, 1), (target_digit + random.randint(-1, 1), 2)]
                    random.shuffle(digits)
                    
                    return self.generate_returned_data(digits, False, True, authProvider)
                
                else:
                    
                    # Won!
                    
                    target_digit = random.randint(0, 9)
                    digits = [(target_digit, 0), (target_digit, 1), (target_digit, 2)]
                    
                    return self.generate_returned_data(digits, True, True, authProvider)
                
            else:
                
                # Should not trick

                digits = [(random.randint(0, 9), 0), (random.randint(0, 9), 1), (random.randint(0, 9), 2)]
                random.shuffle(digits)
                won = (digits[0][0] == digits[1][0] == digits[2][0])
                
                return self.generate_returned_data(digits, won, won, authProvider) # If won, try the trick effect!
        except Exception as e:
            print(f"Failed: {e}")
            return jsonify(success=False, message="Internal server error"), 500
    
    def redeem_token_route(self, authProvider: "AuthProvider") -> tuple[Response, int]:
        
        tokenData = authProvider.check_token(request)
        
        jsonData = request.get_json()
        if not jsonData: return jsonify(success=False, message="No JSON data"), 400
        if tokenData == None: return jsonify(success=False, message="Invalid token"), 401
        
        rewardToken = jsonData.get("rewardToken")
        
        if rewardToken == None: return jsonify(success=False, message="No reward token"), 400

        payload = None
        try:
            payload = jwt.decode(rewardToken, JWT_GAMBLING_REWARD_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify(success=False, message="Invalid token"), 401
        except jwt.InvalidTokenError:
            return jsonify(success=False, message="Invalid token"), 401
        
        userId = payload.get("userId")
        tokenId = payload.get("tokenId")
        reward = payload.get("reward")
        if userId == None or tokenId == None or reward == None:
            return jsonify(success=False, message="Invalid reward token"), 400
        if userId != tokenData.get("id"):
            return jsonify(success=False, message="You do not own this reward token"), 401

        if self.does_token_id_exist(tokenId) == False:
            return jsonify(success=False, message="Invalid reward token"), 401
        
        rewardTokenDbData = self.gambling_db.read_row_from_table("tokens", "id", tokenId, ["valid"])
        
        if rewardTokenDbData == None:
            return jsonify(success=False, message="Unknown read error"), 500
        
        if rewardTokenDbData.get("valid") != 1:
            print(f"Got: {rewardTokenDbData}")
            return jsonify(success=False, message="Invalid reward token, already used"), 401
        
        # Give reward
        
        userDbData = authProvider.db_provider.read_user_data(id=userId)
        if userDbData == None:
            return jsonify(success=False, message="User not found"), 500
        
        newCoins = userDbData.get("coins") + reward
        
        authProvider.db_provider.change_user_data({
            "coins": newCoins
        }, id=userId)
        
        self.gambling_db.change_row_in_table("tokens", {
            "valid": 0
        }, "id", tokenId)
        
        
        return jsonify(success=False, message="OK"), 200
                
        