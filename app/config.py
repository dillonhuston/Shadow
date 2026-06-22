import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Paths
    ENCRYPTED_FILE_PATH = os.getenv('ENCRYPTED_FILE_PATH', './encrypted_files')
    
    # PBKDF2 parameters
    PBKDF2_ITERATIONS = int(os.getenv('PBKDF2_ITERATIONS', 100000))
    PBKDF2_DK_LEN = int(os.getenv('PBKDF2_DK_LEN', 32))
    
    # Encryption component sizes
    KEY_HASH_SIZE = int(os.getenv('KEY_HASH_SIZE', 32))
    NONCE_SIZE = int(os.getenv('NONCE_SIZE', 16))
    TAG_SIZE = int(os.getenv('TAG_SIZE', 16))
    
    # File naming
    ENCRYPTED_FILE_EXTENSION = os.getenv('ENCRYPTED_FILE_EXTENSION', '.enc')

    
    MIMETYPES = {
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'zip': 'application/zip',
            'csv': 'text/csv',
            'json': 'application/json',
            'xml': 'application/xml'
        }