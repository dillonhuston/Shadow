import os
import logging
from sqlalchemy.orm import Session

from app.config import Config
from app.models.file import File as FileModel   

logger = logging.getLogger(__name__)


class FileStorageService:

    @staticmethod
    def get_dir_files(user_id: int, db: Session):
        """Fixed: Now requires db session (no more .query on model)"""
        files = db.query(FileModel).filter_by(user_id=user_id).all()
        return [file.filename for file in files]

    @staticmethod
    def save_file(file_data: bytes, filename: str):
        if not file_data:
            raise ValueError("No file data provided.")

        path = os.path.join(Config.ENCRYPTED_FILE_PATH, filename)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as file:
                file.write(file_data)
            logger.info(f"File saved: {path}")
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            raise

    @staticmethod
    def retrieve_file(filepath: str) -> bytes:
        try:
            with open(filepath, 'rb') as file:
                data = file.read()
            logger.info(f"File retrieved: {filepath}")
            return data
        except Exception as e:
            logger.error(f"Failed to retrieve {filepath}: {e}")
            raise

    @staticmethod
    def delete_file(filepath: str):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File deleted: {filepath}")
        except Exception as e:
            logger.error(f"Failed to delete {filepath}: {e}")
            raise