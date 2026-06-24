import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.config import Config
from app.models.file import File as FileModel   
from app.exceptions.exceptions import FileError

logger = logging.getLogger(__name__)

class FileStorageService:

    @staticmethod
    def get_dir_files(user_id: int, db: Session):
        """Retrieves list of filenames associated with a user."""
        files = db.query(FileModel).filter_by(user_id=user_id).all()
        return [file.filename for file in files]

    async def save_file(self, file_data: bytes, filename: str):
        if not file_data:
            raise FileError("No file data provided.")

        file_path = Path(Config.ENCRYPTED_FILE_PATH) / filename
        
        try:
            # Ensure the directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write binary data
            file_path.write_bytes(file_data)
            logger.info(f"File saved: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            raise FileError(f"IO Error: {e}")

    @staticmethod
    def retrieve_file(filepath: str) -> bytes:
        path = Path(filepath)
        try:
            if not path.exists():
                raise FileError(f"File not found: {filepath}")
            
            data = path.read_bytes()
            logger.info(f"File found: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to find {filepath}: {e}")
            raise FileError(f"IO Error: {e}")

    @staticmethod
    def delete_file(filepath: str):
        path = Path(filepath)
        try:
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {filepath}")
        except Exception as e:
            logger.error(f"Failed to delete {filepath}: {e}")
            raise FileError(f"IO Error: {e}")