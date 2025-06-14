from src.db_provider import DatabaseProvider
from src.custom_types import *
from src.config import JWT_SECRET_KEY, CAPTCHA_SECRET
from src.encryption_tunnel import EncryptionTunnel

import time
import random
import bcrypt
import datetime
import jwt
import traceback
import requests
import re
import hashlib
import base64
import json

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from flask import make_response, jsonify
from flask import Request, request
from flask import Response

from typing import NoReturn
from typing import cast
from typing import Any

SLEEP_DURATION_MIN = 0.7
SLEEP_DURATION_MAX = 1.4

TOKEN_EXPIRY_TIME = datetime.timedelta(days=7)
TOKEN_EXPIRY_INT = (60 * 60 * 24) * 7



class AuthProvider:

    def __init__(self, db_provider: DatabaseProvider):
        '''
        Authentication class
        '''
        self.db_provider = db_provider
        self.safe_tunnel = EncryptionTunnel()
    
    def generateToken(self, userData: AuthenticationDataReturnType, transfer: bool)->tuple[HTTPRequestResponseDict, str | None]:
        '''
        Generates JWT token (internal)
        '''
        payload = {
            "username": userData['username'],
            "id": userData['id'], # Database entry ID
            'exp': datetime.datetime.utcnow() + TOKEN_EXPIRY_TIME
        }
        print(f"User: {payload["username"]}")

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        
        if transfer == False: 
            output: HTTPRequestResponseDict = {
                'success': True,
                'message': "OK",
                'httpStatus': 200
            }

            return output, token
        else:
            output_withtransfer: HTTPRequestResponseDict = {
                'success': True,
                'message': "OK",
                'httpStatus': 200,
                "data": token
            }

            return output_withtransfer, None

    def create_public_and_private_key(self, user_password: str, user_data: AuthenticationDataReturnType, force: bool=False)->None:
        '''
        Creates public & private key for message encryption feature
        '''
        try:
            if user_data["publicKey"] != None and user_data["privateKey"] != None:
                if force == False:
                    print("Already has public and private keys")
                    return
            key = RSA.generate(2048)

            private_key = key.export_key()
            public_key_bytes: bytes = key.publickey().export_key()

            private_key_str = private_key.decode()  # Convert bytes to string
            public_key_str = public_key_bytes.decode()   # Convert bytes to string
            print(public_key_str, private_key_str)

            nonce = get_random_bytes(12)  # 12 bytes is recommended for GCM

            password_hashed = hashlib.sha256(user_password.encode()).digest()
            cipher = AES.new(password_hashed, AES.MODE_GCM, nonce=nonce)
            ct, tag = cipher.encrypt_and_digest(private_key_str.encode())
            

            encrypted = nonce + tag + ct
            print("Encrpyted AES key:")
            print(encrypted)

            self.db_provider.change_user_data({
                "favorites": user_data["favorites"],
                "id": user_data["id"],
                "iv": None,
                "ownedThemes": user_data["ownedThemes"],
                "password": user_data["password"],
                "privateKey": encrypted,
                "publicKey": public_key_str,
                "username": user_data["username"]
            }, id=user_data["id"])
        except Exception as e:
            print("Failed to create public & private key: ", traceback.format_exc())
        

    def auth(self, username: str, password: str, transfer: bool) -> tuple[HTTPRequestResponseDict, str|None]:
        '''
        Authenticates user and creates token. Login.
        '''
        try:
            print("AUTH")
            user_data: AuthenticationDataReturnType | None = self.db_provider.read_user_data(username=username)
            if (user_data == None):
                time.sleep(random.uniform(SLEEP_DURATION_MIN, SLEEP_DURATION_MAX))
                print(f"Username not found!")
                return {
                    'success': False,
                    'message': "Invalid credentials",
                    'httpStatus': 401
                }, None
            
            hashed_db_password: str = user_data["password"]

            if bcrypt.checkpw(password.encode(), hashed_db_password.encode()) == False:
                print(f"Incorrect password")
                return {
                    'success': False,
                    'message': "Invalid credentials",
                    'httpStatus': 401
                }, None
            self.create_public_and_private_key(password, user_data)
            out, tok = self.generateToken(user_data, transfer)
            print("GENERATED THE FUCKING TOKEN")
            return out, tok
             
        except Exception as e:
            print("Failed AUTH: ", e)
            return {
                'success': False,
                'message': "Internal server error",
                'httpStatus': 500
            }, None
    def check_token(self, request: Request) -> AuthenticationToken | None:
        '''
        Checks user token and returns payload
        '''
        token = request.cookies.get(
            
            'jwt')

        if not token:
            try:
                data = request.get_json()
                token = data.get('token')
            except: print("Failed to get JSON", traceback.format_exc())
        if not token:
            try:
                print(request.headers)
                token = request.headers.get("Authorization")
                if token == None:
                    raise ValueError("No token in headers")
                print(token)
                token = token[7:]  # Strip 'Bearer '
                print(str(token))
            except: print("Failed to get headers ", traceback.format_exc())
        if not token:
            print("No token???")
            return None
        try:
            decoded_payload: AuthenticationToken|NoReturn = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            print(decoded_payload)
            return decoded_payload
        except jwt.ExpiredSignatureError:
            print("Expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid")
            return None
    def register(self, username: str, password: str, captcha: str, privateKeyPassword: str, verifyCaptcha: bool = True) -> HTTPRequestResponseDict:
        '''
        Registers a new user
        '''
        try:
            if len(username) > 31:
                print(f"Username is too long!")
                return {
                    'success': False,
                    'message': "Username too long",
                    'httpStatus': 400
                }
            if self.is_valid_string(username) == False:
                print(f"Username invalid characters!")
                return {
                    'success': False,
                    'message': "Username can only contain letters, numbers, and underscores.",
                    'httpStatus': 400
                }
            if verifyCaptcha == True and self.verify_captcha(captcha) == False:
                return {
                    'success': False,
                    'message': "Invalid CAPTCHA",
                    'httpStatus': 400
                }
            if len(username) < 4:
                print(f"Username too short!")
                return {
                    'success': False,
                    'message': "Username must be atleast 4 characters",
                    'httpStatus': 400
                }
            if len(password) < 6:
                print(f"Password too short!")
                return {
                    'success': False,
                    'message': "Password must be atleast 6 characters",
                    'httpStatus': 400
                }
            username = username.lower()
            data: AuthenticationDataReturnType | None = self.db_provider.read_user_data(username=username)
            if (data != None):
                print(f"Username i use")
                return {
                    'success': False,
                    'message': "Username in use",
                    "httpStatus": 409
                }
            hashed_password: str = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode()
            self.db_provider.add_user({
                "username": username,
                "favorites": "[]",
                "ownedThemes": "[]",
                "password": hashed_password,
                "publicKey": "b",
                "privateKey": "b",
                "iv": "b"
            })
            self.create_public_and_private_key(privateKeyPassword, cast(AuthenticationDataReturnType, self.db_provider.read_user_data(username=username)), force=True)
            print(f"New user OK")
            return {
                'success': True,
                'message': "OK",
                'httpStatus': 200
            }
        except Exception as e:
            print("Failed AUTH:", traceback.format_exc())
            return {
                'success': False,
                'message': "Internal server error",
                'httpStatus': 500
            }
    
    @staticmethod
    def is_valid_string(s: str)->bool:
        return bool(re.match(r'^[a-zA-Z0-9_]+$', s))

    @staticmethod
    def verify_captcha(token: str) -> bool:
        try:
            response = requests.post('https://hcaptcha.com/siteverify', {"secret": CAPTCHA_SECRET, 'response': token})
            json = response.json()
            if json.get("success") == True:
                print("CAPTCHA: Ok")
                return True
            else:
                print("CAPTCHA: Not successfull")
                return False
        except Exception as e:
            print("CAPTCHA: Failed: ", traceback.format_exc())
            return False
    def search_users(self, search_term: str) -> HTTPRequestResponseDict:
        '''
        Search API for users
        '''
        if search_term == None or search_term == '':
            return {
                "success": True,
                "message": "OK",
                "data": [],
                "httpStatus": 200
            }
        try:
            print(search_term)
            c = self.db_provider.db.database.cursor()
            c.execute('''
                SELECT * FROM users
                WHERE username LIKE ?
            ''', ('%' + search_term + '%',))

            # Fetch and print the results
            rows = c.fetchall()
            c.close()
            final_data: dict[str, int] = {}
            for row in rows:

                final_data[row[1]] = row[0]

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
    def auth_route(self)->tuple[Response, int]:
        try:
            requestData = request.get_json()
            iv: str | None = requestData.get("iv")
            ct: str | None = requestData.get("ct")
            k: str | None = requestData.get("k")
            if (iv == None or ct == None or k == None):
                return jsonify(success=False, message="Bad request"), 400
            decrypted = self.safe_tunnel.decrypt_body(base64.b64decode(ct.encode()), base64.b64decode(iv.encode()), base64.b64decode(k.encode()))
            djson = json.loads(decrypted)

            print("AUH AUTH AUTH AUTH", flush=True)
            print("*")

            username = djson.get('username')
            password = djson.get('password')
            transfer = djson.get('transfer')

            if (username == None or password == None):
                return jsonify(success=False, message="Bad request"), 400

            # Get the username in the JSON file
            
            out, tok = self.auth(username, password, transfer or False)
            if tok:
                resp = make_response(jsonify(out))
                resp.set_cookie("jwt", tok, max_age=TOKEN_EXPIRY_INT, httponly=True, secure=False)
                return resp, out['httpStatus']
            return jsonify(out), out['httpStatus']
        except Exception as e:
            print("Failed: ", e)
            return jsonify(success=False, message="Unknown error", errorId="UKW_ERR"), 500
    
    def register_route(self)->tuple[Response, int]:
        try:
            requestData = request.get_json()
            iv: str | None = requestData.get("iv")
            ct: str | None = requestData.get("ct")
            k: str | None = requestData.get("k")
            if (iv == None or ct == None or k == None):
                return jsonify(success=False, message="Bad request"), 400
            decrypted = self.safe_tunnel.decrypt_body(base64.b64decode(ct.encode()), base64.b64decode(iv.encode()), base64.b64decode(k.encode()))
            djson = json.loads(decrypted)
            username = djson.get('username')
            password = djson.get('password')
            captcha = djson.get('captcha')
            privateKeyPassword = djson.get('privateKeyPassword')

            if username == None or password == None or captcha == None or privateKeyPassword == None:
                return jsonify(success=False, message="Bad request"), 400

            auth = self.register(username, password, captcha, privateKeyPassword)
            

            return jsonify(auth), auth['httpStatus']
        except Exception as e:
            print("it fucking Failed: ", e)
            return jsonify(success=False, message="Unknown error", errorId="UKW_ERR"), 500

    def search_users_route(self)->tuple[Response, int]:
        try:
            search_term = request.args.get("search")
            if search_term == None:
                return jsonify(success=False, message="No search term provided"), 400

            out = self.search_users(search_term)
            return jsonify(out), out["httpStatus"]
        except Exception as e:
            print("Failed: ", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500

__all__ = ['AuthProvider']