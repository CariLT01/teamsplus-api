from src.db_provider import DatabaseProvider
from src.custom_types import *
from src.auth_provider import AuthProvider
from src.encryption_tunnel import EncryptionTunnel

from flask import Response, request, jsonify

import time

start = time.time()

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256

end = time.time()

print(f"Crypto import time: {end - start}s")

import hashlib
import base64
import traceback
import json

class EncryptionProvider:

    def __init__(self, db_provider: DatabaseProvider):
        '''
        Encryption provider
        '''
        self.db_provider = db_provider
        self.safe_tunnel = EncryptionTunnel()
    

    def encrypt(self, to_user_ids: list[int], body: str, password: str, tokenData: AuthenticationToken) -> EncryptionProviderResultDict:
        '''
        Encrypts message
        '''
        body.encode().decode() # Ensure invalid characters cause error
        myUserId = tokenData["id"]
        #print(f"My user id: {myUserId}")
        my_user_data: AuthenticationDataReturnType | None = self.db_provider.read_user_data(id=myUserId)
        if my_user_data == None:
            raise Exception("User data not found")
        myPrivateKey: bytes = my_user_data["privateKey"]
        #print(myPrivateKey)
        nonce = myPrivateKey[:12]
        tag = myPrivateKey[12:28]
        ct = myPrivateKey[28:]
        hashedPassword = hashlib.sha256(password.encode()).digest()
        #print("Hashed password:")
        #print(hashedPassword)
        #print(f"Len: {len(hashedPassword)}")
        #print("IV:")
        #print(nonce)
        #print(f"Len: {len(nonce)}")
        cipher = AES.new(hashedPassword, AES.MODE_GCM, nonce=nonce)
        pt = cipher.decrypt_and_verify(ct, tag)
        my_privateKeyImported = RSA.import_key(pt)

        aes_key = get_random_bytes(32)
        nonce2: bytes = get_random_bytes(12)


        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce2)
        ct, tag = cipher.encrypt_and_digest(body.encode())
        iv = nonce2 + tag # 12 bytes + 16 bytes
        

        hashed_body = SHA256.new(body.encode())
        signer = pss.new(my_privateKeyImported)
        signature = signer.sign(hashed_body)

        signature_b64 = base64.b64encode(signature).decode()
        encrypted_body_b64 = base64.b64encode(ct).decode()
        iv_b64 = base64.b64encode(iv).decode()

        #print("Encrypted body B64: ", encrypted_body_b64)
        #print("IV B64: ", iv_b64)
        #print("Signature B64: ", signature_b64)
        
        #print("Message signature: ", signature)
        
        dest_keys: dict[int, str] = {}

        # Include self
        if not (tokenData["id"] in to_user_ids):
            to_user_ids.append(tokenData["id"])

        failed = []

        for user_id_dest in to_user_ids:
            try:
                dest_user_data = self.db_provider.read_user_data(id=user_id_dest)

                if dest_user_data == None:
                    print("Failed to encrypt for: ", user_id_dest)
                    failed.append(user_id_dest)
                    continue
                
                dest_public_key: str = dest_user_data["publicKey"]
                

                if (dest_public_key == None or myPrivateKey == None):
                    print("Failed to encrypt for: ", user_id_dest)
                    failed.append(user_id_dest)
                    continue


                dest_publicKeyImported: RSA.RsaKey = RSA.import_key(dest_public_key)
                


                cipher_2: PKCS1_OAEP.PKCS1OAEP_Cipher = PKCS1_OAEP.new(dest_publicKeyImported)
                ciphertext = cipher_2.encrypt(aes_key)   

                encrypted_aes_b64 = base64.b64encode(ciphertext).decode()

                #print(f"Encrypted key for {user_id_dest}:", encrypted_aes_b64)


                dest_keys[user_id_dest] = encrypted_aes_b64
            except Exception as e:
                print(e)
                failed.append(user_id_dest)


        final_output: EncryptionProviderDataDict = {
            "body": encrypted_body_b64,
            "iv": iv_b64,
            "signature": signature_b64,
            "keys": dest_keys,
            "author": tokenData["id"]
        }

        note: str | None = f"Failed to encrypt for: {failed}"
        if len(failed)==0:note=None


        return {
            "success": True,
            "message": "OK",
            "data": final_output,
            "httpStatus": 200,
            "note": note
        }

    def decrypt(self, signature: str, body: str, iv: str, aes_keys: dict[str, str], tokenData: AuthenticationToken, password: str, author: int) -> HTTPRequestResponseDict:
        '''
        Decrypts message
        '''
        try:
            aes_key: str | None = aes_keys.get(str(tokenData["id"]))
            #print(aes_keys, tokenData["id"])
            if aes_key == None:
                return {
                    "success": False,
                    "message": "Message not dedicated to user",
                    "httpStatus": 401
                }

            body_bytes = base64.b64decode(body)
            key_bytes = base64.b64decode(aes_key)
            iv_bytes = base64.b64decode(iv)
            signature_bytes = base64.b64decode(signature)

            # Init verify

            author_userData = self.db_provider.read_user_data(id=author)
            if author_userData == None:
                raise Exception("Author data not found")
            
            author_publicKey = author_userData["publicKey"]
            auythor_public_key_loaded = RSA.import_key(author_publicKey)
            verifier = pss.new(auythor_public_key_loaded)

            

            # Get private key

            myUserId = tokenData["id"]
            my_user_data: AuthenticationDataReturnType | None = self.db_provider.read_user_data(id=myUserId)
            if my_user_data == None:
                raise Exception("User data not found")
            myPrivateKey: bytes = my_user_data["privateKey"]
            #print(myPrivateKey)
            nonce = myPrivateKey[:12]
            tag = myPrivateKey[12:28]
            ct = myPrivateKey[28:]



            hashedPassword = hashlib.sha256(password.encode()).digest()
            cipher = AES.new(hashedPassword, AES.MODE_GCM, nonce=nonce)  # nonce replaces iv
            pt = cipher.decrypt_and_verify(ct, tag)

            #print(pt)

            my_privateKeyImported = RSA.import_key(pt)

            # Decrypt the AES key
            
            #print(key_bytes)

            decipher = PKCS1_OAEP.new(my_privateKeyImported)
            plaintext = decipher.decrypt(key_bytes)

            #print("Plaintext AES KEY: ", plaintext)

            # Decrypt the fucking message
            nonce = iv_bytes[:12] # 12 bytes
            tag = iv_bytes[12:] # 16 bytes
            cipher = AES.new(plaintext, AES.MODE_GCM, nonce=nonce)
            pt = cipher.decrypt_and_verify(body_bytes, tag)

            #print("Decrpted message: ", pt)
            #print(pt.decode())

            hash_obj = SHA256.new(pt)
            verifier.verify(hash_obj, signature_bytes)
            #print("Signature is valid")

            return {
                "success": True,
                "message": "OK",
                "httpStatus": 200,
                "data": pt.decode()
            }

        except Exception as e:
            print("Decryption failed: ", traceback.format_exc())
            return {
                "success": False,
                "message": "Internal server error",
                "httpStatus": 500
            }
    def encrypt_route(self, authProvider: AuthProvider)->tuple[Response, int]:
        try:
            tokenData = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
            
            requestData = request.get_json()



            iv: str | None = requestData.get("iv")
            ct: str | None = requestData.get("ct")
            k: str | None = requestData.get("k")

            #dest_user_id = requestData.get("destination")
            #body = requestData.get("body")
            #password = requestData.get("pwd")

            if (iv == None or ct == None or k == None):
                return jsonify(success=False, message="Bad request"), 400
            
            decrypted = self.safe_tunnel.decrypt_body(base64.b64decode(ct.encode()), base64.b64decode(iv.encode()), base64.b64decode(k.encode()))
            djson = json.loads(decrypted)

            dest_user_id = djson.get("destination")
            body = djson.get("body")
            password = djson.get("pwd")

            if (dest_user_id == None or body == None or password == None):
                return jsonify(success=False, message="Bad request: after decryption"), 400 

            output = self.encrypt(dest_user_id, body, password, tokenData)

            return jsonify(output), output["httpStatus"]


        except Exception as e:
            print("Failed: ", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500


    def decrypt_route(self, authProvider: AuthProvider)->tuple[Response, int]:

        try:
            tokenData = authProvider.check_token(request)
            if tokenData == None:
                return jsonify(success=False, message="Unauthorized", errorId="UNAUTHORIZED"), 401
            if tokenData.get("username") == None:
                return jsonify(success=False, message="Invalid token - Username field not found", errorId="UNAUTHORIZED"), 401
            requestData = request.get_json()

            iv: str | None = requestData.get("iv")
            ct: str | None = requestData.get("ct")
            k: str | None = requestData.get("k")


            if (iv == None or ct == None or k == None or k == None):
                return jsonify(success=False, message="Bad request"), 400

            
            decrypted = self.safe_tunnel.decrypt_body(base64.b64decode(ct.encode()), base64.b64decode(iv.encode()), base64.b64decode(k.encode()))
            djson = json.loads(decrypted)

            body = djson.get("body")
            password = djson.get("pwd")
            signature = djson.get("signature")
            iv = djson.get("iv")
            key = djson.get("key")
            author = djson.get("author")

            if (body == None or password == None or signature == None or iv == None or key == None or author == None):
                return jsonify(success=False, message="Bad request"), 400

            output = self.decrypt(signature, body, iv, key, tokenData, password, author)
            enc: bytes
            eiv: bytes
            enc, eiv = self.safe_tunnel.encrypt_body(json.dumps(output).encode(), base64.b64decode(k))



            return jsonify(ct=base64.b64encode(enc).decode(), iv=base64.b64encode(eiv).decode()), output["httpStatus"]


        except Exception as e:
            print("Failed: ", traceback.format_exc())
            return jsonify(success=False, message="Internal server error"), 500