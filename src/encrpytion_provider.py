from src.db_provider import DatabaseProvider
from src.types import *

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256


import hashlib
import base64
import traceback

class EncryptionProvider:

    def __init__(self, db_provider: DatabaseProvider):
        self.db_provider = db_provider
    
    def encrypt(self, to_user_ids: list[int], body: str, password: str, tokenData: AuthenticationToken) -> AuthProviderResultDict:
        body.encode().decode() # Ensure invalid characters cause error
        myUserId = tokenData["id"]
        my_user_data = self.db_provider.read_authentication_data_for_user_or_id(id=myUserId)
        myPrivateKey: str = my_user_data["privateKey"]
        print(myPrivateKey)
        nonce = myPrivateKey[:12]
        tag = myPrivateKey[12:28]
        ct = myPrivateKey[28:]
        hashedPassword = hashlib.sha256(password.encode()).digest()
        print("Hashed password:")
        print(hashedPassword)
        print(f"Len: {len(hashedPassword)}")
        print("IV:")
        print(nonce)
        print(f"Len: {len(nonce)}")
        cipher = AES.new(hashedPassword, AES.MODE_GCM, nonce=nonce)
        pt = cipher.decrypt_and_verify(ct, tag)
        my_privateKeyImported = RSA.import_key(pt)

        aes_key = get_random_bytes(32)
        nonce = get_random_bytes(12)


        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        ct, tag = cipher.encrypt_and_digest(body.encode())
        iv = nonce + tag # 12 bytes + 16 bytes
        

        hashed_body = SHA256.new(body.encode())
        signer = pss.new(my_privateKeyImported)
        signature = signer.sign(hashed_body)

        signature_b64 = base64.b64encode(signature).decode()
        encrypted_body_b64 = base64.b64encode(ct).decode()
        iv_b64 = base64.b64encode(iv).decode()

        print("Encrypted body B64: ", encrypted_body_b64)
        print("IV B64: ", iv_b64)
        print("Signature B64: ", signature_b64)
        
        print("Message signature: ", signature)
        
        dest_keys: dict[int, str] = {}

        # Include self
        if not (tokenData["id"] in to_user_ids):
            to_user_ids.append(tokenData["id"])

        failed = []

        for user_id_dest in to_user_ids:
            try:
                dest_user_data = self.db_provider.read_authentication_data_for_user_or_id(id=user_id_dest)

                if dest_user_data == None:
                    print("Failed to encrypt for: ", user_id_dest)
                    failed.append(user_id_dest)
                    continue
                
                dest_public_key: str = dest_user_data["publicKey"]
                

                if (dest_public_key == None or myPrivateKey == None):
                    print("Failed to encrypt for: ", user_id_dest)
                    failed.append(user_id_dest)
                    continue


                dest_publicKeyImported = RSA.import_key(dest_public_key)
                


                cipher = PKCS1_OAEP.new(dest_publicKeyImported)
                ciphertext = cipher.encrypt(aes_key)   

                encrypted_aes_b64 = base64.b64encode(ciphertext).decode()

                print(f"Encrypted key for {user_id_dest}:", encrypted_aes_b64)


                dest_keys[user_id_dest] = encrypted_aes_b64
            except Exception as e:
                print(e)
                failed.append(user_id_dest)


        final_output = {
            "body": encrypted_body_b64,
            "iv": iv_b64,
            "signature": signature_b64,
            "keys": dest_keys,
            "author": tokenData["id"]
        }

        note = f"Failed to encrypt for: {failed}"
        if len(failed)==0:note=None


        return {
            "success": True,
            "message": "OK",
            "data": final_output,
            "httpStatus": 200,
            "note": note
        }

    def decrypt(self, signature: str, body: str, iv: str, aes_keys: dict[int, str], tokenData: AuthenticationToken, password: str, author: int) -> AuthProviderResultDict:
        try:
            aes_key = aes_keys.get(str(tokenData["id"]))
            print(aes_keys, tokenData["id"])
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

            author_userData = self.db_provider.read_authentication_data_for_user_or_id(id=author)
            if author_userData == None:
                raise Exception("Author data not found")
            
            author_publicKey = author_userData["publicKey"]
            auythor_public_key_loaded = RSA.import_key(author_publicKey)
            verifier = pss.new(auythor_public_key_loaded)

            

            # Get private key

            myUserId = tokenData["id"]
            my_user_data = self.db_provider.read_authentication_data_for_user_or_id(id=myUserId)
            myPrivateKey: str = my_user_data["privateKey"]
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

            print("Decrpted message: ", pt)
            #print(pt.decode())

            hash_obj = SHA256.new(pt)
            verifier.verify(hash_obj, signature_bytes)
            print("Signature is valid")

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
