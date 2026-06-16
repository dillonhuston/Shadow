import os
import base64
import hashlib
import logging

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from app.config import Config

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Custom exception for encryption/decryption errors."""
    pass


class EncryptionService:
    """Handles file encryption and decryption using AES-EAX."""

    @staticmethod
    def _ensure_bytes_key(key: str | bytes | bytearray) -> bytes:
        """Safely convert key to bytes."""
        if isinstance(key, bytes):
            return key
        elif isinstance(key, bytearray):
            return bytes(key)
        elif isinstance(key, str):
            return key.encode('utf-8')
        else:
            raise EncryptionError("Invalid key type")

    @staticmethod
    def _ensure_str_key(key: str | bytes | bytearray) -> str:
        """Safely convert key to string for PBKDF2."""
        if isinstance(key, str):
            return key
        elif isinstance(key, bytes):
            return key.hex()
        elif isinstance(key, bytearray):
            return bytes(key).hex()
        else:
            raise EncryptionError("Invalid key type")

    @staticmethod
    def encrypt(data: str | bytes, filename: str, user_id: str, key: str | bytes | bytearray) -> str:
        try:
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data

            # Convert key to string for PBKDF2
            key_str = EncryptionService._ensure_str_key(key)

            # Derive key
            salt = hashlib.sha256(user_id.encode('utf-8')).digest()
            derived_key = PBKDF2(key_str, salt, dkLen=Config.PBKDF2_DK_LEN, count=Config.PBKDF2_ITERATIONS)
            derived_key = derived_key[:Config.PBKDF2_DK_LEN]

            key_hash = hashlib.sha256(derived_key).digest()

            # Encrypt
            cipher = AES.new(derived_key, AES.MODE_EAX)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(data_bytes)

            # Unique filename
            base_name = f"{hashlib.sha1(user_id.encode('utf-8')).hexdigest()[:8]}_{filename}{Config.ENCRYPTED_FILE_EXTENSION}"
            encrypted_filename = base_name
            counter = 1
            file_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)

            while os.path.exists(file_path):
                encrypted_filename = f"{base_name.split(Config.ENCRYPTED_FILE_EXTENSION)[0]}_{counter}{Config.ENCRYPTED_FILE_EXTENSION}"
                file_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)
                counter += 1

            os.makedirs(Config.ENCRYPTED_FILE_PATH, exist_ok=True)

            with open(file_path, 'wb') as f:
                f.write(key_hash + nonce + tag + ciphertext)

            logger.info(f"File encrypted: {encrypted_filename}")
            return encrypted_filename

        except Exception as e:
            logger.error(f"Encryption failed for {filename}: {e}")
            raise EncryptionError(f"Encryption failed: {str(e)}")

    @staticmethod
    def decrypt(encrypted_filename: str, user_id: str, key: str | bytes | bytearray) -> bytes:
        """
        Decrypt a file and return the raw bytes.
        Returns bytes directly instead of base64 encoded string.
        """
        try:
            file_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)
            if not os.path.exists(file_path):
                raise EncryptionError("File not found")

            # Convert key to string for PBKDF2
            key_str = EncryptionService._ensure_str_key(key)

            salt = hashlib.sha256(user_id.encode('utf-8')).digest()
            derived_key = PBKDF2(key_str, salt, dkLen=Config.PBKDF2_DK_LEN, count=Config.PBKDF2_ITERATIONS)
            derived_key = derived_key[:Config.PBKDF2_DK_LEN]
            key_hash = hashlib.sha256(derived_key).digest()

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            min_size = Config.KEY_HASH_SIZE + Config.NONCE_SIZE + Config.TAG_SIZE
            if len(encrypted_data) < min_size:
                raise EncryptionError("Encrypted data too short")

            stored_key_hash = encrypted_data[:Config.KEY_HASH_SIZE]
            nonce = encrypted_data[Config.KEY_HASH_SIZE:Config.KEY_HASH_SIZE + Config.NONCE_SIZE]
            tag = encrypted_data[Config.KEY_HASH_SIZE + Config.NONCE_SIZE:Config.KEY_HASH_SIZE + Config.NONCE_SIZE + Config.TAG_SIZE]
            ciphertext = encrypted_data[Config.KEY_HASH_SIZE + Config.NONCE_SIZE + Config.TAG_SIZE:]

            if stored_key_hash != key_hash:
                raise EncryptionError("Key mismatch detected")

            cipher = AES.new(derived_key, AES.MODE_EAX, nonce=nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

            return decrypted_data

        except EncryptionError:
            raise
        except Exception as e:
            logger.error(f"Decryption failed for {encrypted_filename}: {e}")
            raise EncryptionError(f"Decryption failed: {str(e)}")