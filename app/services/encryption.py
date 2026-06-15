from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from app.config import Config
import base64
import os
import hashlib

class EncryptionService:
    class EncryptionError(Exception):
        pass

    
    def encrypt(data, filename, user_id, key):
        try:
            if isinstance(data, str):
                data_bytes = base64.b64decode(data)
            else:
                data_bytes = data

            if not isinstance(key, bytes):
                key = key.encode('utf-8')
            salt = hashlib.sha256(user_id.encode('utf-8')).digest()
            print(f"Encrypt - user_id: {user_id}, salt (hex): {salt.hex()}")
            derived_key = PBKDF2(key, salt, dkLen=32, count=100000)
            derived_key = derived_key[:32]
            key_hash = hashlib.sha256(derived_key).digest()
            print(f"Encrypt - raw key: {key.hex() if isinstance(key, bytes) else key}, derived key (hex): {derived_key.hex()}, key_hash (hex): {key_hash.hex()}")

            cipher = AES.new(derived_key, AES.MODE_EAX)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(data_bytes)

            base_name = f"{hashlib.sha1(user_id.encode('utf-8')).hexdigest()[:8]}_{filename}.enc"
            encrypted_filename = base_name
            counter = 1
            file_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)
            while os.path.exists(file_path):
                encrypted_filename = f"{base_name.split('.enc')[0]}_{counter}.enc"
                file_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)
                counter += 1

            os.makedirs(Config.ENCRYPTED_FILE_PATH, exist_ok=True)

            with open(file_path, 'wb') as f:
                f.write(key_hash + nonce + tag + ciphertext)

            return encrypted_filename

        except (base64.binascii.Error, ValueError, OSError) as e:
            raise EncryptionService.EncryptionError(f"Encryption failed: {str(e)}")

    
    def decrypt(encrypted_filename, user_id, key):
        try:
            file_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)

            if not os.path.exists(file_path):
                raise EncryptionService.EncryptionError("File not found")

            if not isinstance(key, bytes):
                key = key.encode('utf-8')
            salt = hashlib.sha256(user_id.encode('utf-8')).digest()
            print(f"Decrypt - user_id: {user_id}, salt (hex): {salt.hex()}")
            derived_key = PBKDF2(key, salt, dkLen=32, count=100000)
            derived_key = derived_key[:32]
            key_hash = hashlib.sha256(derived_key).digest()
            print(f"Decrypt - raw key: {key.hex() if isinstance(key, bytes) else key}, derived key (hex): {derived_key.hex()}, key_hash (hex): {key_hash.hex()}")

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            if len(encrypted_data) < 64:
                raise EncryptionService.EncryptionError("Encrypted data too short")

            stored_key_hash = encrypted_data[:32]
            nonce = encrypted_data[32:48]
            tag = encrypted_data[48:64]
            ciphertext = encrypted_data[64:]

            print(f"Decrypt - stored_key_hash: {stored_key_hash.hex()}, computed_key_hash: {key_hash.hex()}")
            if stored_key_hash != key_hash:
                raise EncryptionService.EncryptionError("Key mismatch detected")

            cipher = AES.new(derived_key, AES.MODE_EAX, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            return base64.b64encode(data).decode('utf-8')

        except (OSError, ValueError, EncryptionService.EncryptionError) as e:
            raise EncryptionService.EncryptionError(f"Decryption failed: {str(e)}")