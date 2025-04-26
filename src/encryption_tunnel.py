from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
import traceback
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from typing import Any, cast
from flask import jsonify, Response, request


class EncryptionTunnel:
    def __init__(self) -> None:
        self.publicKey = self._load_public_key()
        self.privateKey = self._load_private_key()
    def _load_private_key(self) -> RSAPrivateKey:
        with open("private_key.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=b"ENCRYPTION_TUNNEL_3"  # Same password used when saving
            )
        f.close()
        return cast(RSAPrivateKey, private_key)
        
    def _load_public_key(self) -> RSAPublicKey:
        with open("public_key.pem", "rb") as f:
            return cast(RSAPublicKey, serialization.load_pem_public_key(f.read()))

    def encryption_handshake_route(self) -> tuple[Response, int]:
        try:
            print(request.data)
            data = request.get_json()

            user_public_key = data.get("publicKey")
            if user_public_key == None:
                return jsonify(success=False, message="Bad request"), 400

            aeskey = os.urandom(32)  # AES-256 key
            user_public_key_obj: RSAPublicKey = serialization.load_pem_public_key(user_public_key.encode())
            ciphertext = user_public_key_obj.encrypt(
                aeskey,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            ciphertext_self = self.publicKey.encrypt(
                aeskey,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            #Signature



            return jsonify(success=True, message="OK", data={
                'k': base64.b64encode(ciphertext).decode(),
                'ks': base64.b64encode(ciphertext_self).decode(),
            }), 200
        except Exception as e:
            print(f"Failed: {traceback.format_exc()}")
            return jsonify(success=False, message="Internal server error"), 500


                

    
    def decrypt_body(self, body: bytes, iv: bytes, originalKey: bytes) -> bytes:

        aesKey: bytes = self.privateKey.decrypt(
            originalKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        aesgcm = AESGCM(aesKey)
        plaintext = aesgcm.decrypt(iv, body, None)  # No associated data




        return plaintext

    def encrypt_body(self, body: bytes, originalKey: bytes) -> tuple[bytes, bytes]:

        aesKey: bytes = self.privateKey.decrypt(
            originalKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        iv = os.urandom(12)  # IV = nonce for AES-GCM

        # Encrypt
        aesgcm = AESGCM(aesKey)
        ciphertext = aesgcm.encrypt(iv, body, associated_data=None)

        return ciphertext, iv