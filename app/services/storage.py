import os
import logging
from app.config import Config
from app.models.file import File

logger = logging.getLogger(__name__)

class FileStorageService:
    @staticmethod
    def get_dir_files(user_id):
        files = File.query.filter_by(user_id=user_id).all()
        return [file.filename for file in files]

    @staticmethod
    def save_file(file_data: bytes, filename: str):
        if not file_data:
            logger.error("No file data provided.")
            raise ValueError("No file data provided.")
        path = os.path.join(Config.ENCRYPTED_FILE_PATH, filename)
        try:
            with open(path, 'wb') as file:
                file.write(file_data)
            logger.info(f"File saved: {path}")
        except Exception as e:

            logger.error(f"Failed to save file {filename}: {e}")
            raise

    @staticmethod
    def retrieve_file(filepath: str) -> bytes:
        try:
            with open(filepath, 'rb') as file:
                data = file.read()
            logger.info(f"File retrieved: {filepath}")
            return data
        
        except Exception as e:
            logger.error(f"Failed to retrieve file {filepath}: {e}")
            raise

