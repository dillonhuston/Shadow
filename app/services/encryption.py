import os
import base64
import hashlib
import logging

from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

from app.config import Config

from app.exceptions.exceptions import EncryptionServiceError

logger = logging.getLogger(__name__)


class EncryptionService:
    """Handles file encryption and decryption using AES-EAX."""

    def _ensure_str_key(self,key: str | bytes | bytearray) -> str:
        """Safely convert key to string for PBKDF2."""
        if isinstance(key, str):
            return key
        elif isinstance(key, bytes):
            return key.hex()
        elif isinstance(key, bytearray):
            return bytes(key).hex()
        else:
            raise EncryptionServiceError("Invalid key type")

    async def encrypt(self, data: str | bytes, filename: str, user_id: str, key: str | bytes | bytearray) -> str:
        try:
            data_bytes = data.encode('utf-8') if isinstance(data, str) else data
            key_str = self._ensure_str_key(key)

            salt = get_random_bytes(16) 
            derived_key = PBKDF2(key_str, salt, dkLen=Config.PBKDF2_DK_LEN, count=Config.PBKDF2_ITERATIONS)

            # Encrypt
            cipher = AES.new(derived_key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(data_bytes)

            #  Handle file path and collisions
            output_dir = Path(Config.ENCRYPTED_FILE_PATH)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            base_name = f"{hashlib.sha1(user_id.encode()).hexdigest()[:8]}_{filename}"
            file_path = output_dir / f"{base_name}{Config.ENCRYPTED_FILE_EXTENSION}"
            
            counter = 1
            while file_path.exists():
                file_path = output_dir / f"{base_name}_{counter}{Config.ENCRYPTED_FILE_EXTENSION}"
                counter += 1

            #  Write
            with file_path.open('wb') as f:
                f.write(salt + cipher.nonce + tag + ciphertext)

            return file_path.name

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionServiceError(f"Encryption failed: {e}")

    async def decrypt(self, encrypted_filename: str, user_id: str, key: str | bytes | bytearray) -> bytes:
        try:
            file_path = Path(Config.ENCRYPTED_FILE_PATH) / encrypted_filename
            with file_path.open('rb') as f:
                encrypted_data = f.read()

            salt = encrypted_data[:16]
            nonce = encrypted_data[16:16 + Config.NONCE_SIZE]
            tag = encrypted_data[16 + Config.NONCE_SIZE:16 + Config.NONCE_SIZE + Config.TAG_SIZE]
            ciphertext = encrypted_data[16 + Config.NONCE_SIZE + Config.TAG_SIZE:]

            key_str = EncryptionService._ensure_str_key(self,key)
            derived_key = PBKDF2(key_str, salt, dkLen=Config.PBKDF2_DK_LEN, count=Config.PBKDF2_ITERATIONS)

            cipher = AES.new(derived_key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionServiceError("Decryption failed. Check key or file integrity.")