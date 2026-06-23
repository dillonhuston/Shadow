import os
import base64
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.utils import secure_filename

from app.models.file import File as FileModel
from app.models.user import User
from app.config import Config
from app.services.encryption import EncryptionService
from app.DatabaseOps.DatabaseRepository import DatabaseOps
from app.exceptions.exceptions import FileError, EncryptionServiceError

class FileService:
    def __init__(self, db_ops: DatabaseOps, encryption_service: EncryptionService) -> None:
        self.db_ops = db_ops
        self.encryption_service = encryption_service

    @staticmethod
    def _get_user_key(user: User) -> str:
        """Safely extract user's key as string."""
        return str(user.key) if user.key is not None else ""

    async def upload_file(self, db: AsyncSession, file_data: bytes, filename: str, user: User):
        """Handle file upload, encryption, and database storage."""
        safe_filename = secure_filename(filename)
        encoded_data = base64.b64encode(file_data).decode('utf-8')
            
        user_key = FileService._get_user_key(user)
            
        encrypted_filename = self.encryption_service.encrypt(
            encoded_data,
            safe_filename,
            str(user.id),
            user_key
        )
            
        new_file = FileModel(
            user_id=str(user.id),
            filename=encrypted_filename,
            filepath=os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename),
            original_filename=safe_filename
        )
        try:
            await self.db_ops.add_file(db, new_file)            
            return {'message': f'{safe_filename} uploaded'}
        except Exception:
            await db.rollback()
            raise

    async def list_files(self, db: AsyncSession, user: User) -> List[dict]:
        """List all files for a user."""
        files_info: List[dict] = []
        user_files = await self.db_ops.GetUserFileByUserid(db, user_id=user.id)
        
        for file_entry in user_files:
            filepath = file_entry.filepath
            if os.path.exists(filepath):
                original_filename = file_entry.original_filename
                filename = original_filename if original_filename else file_entry.filename
                created_at = file_entry.created_at.isoformat() if file_entry.created_at is not None else None
                file_id = file_entry.id
                
                files_info.append({
                    'id': file_id,  
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'created_at': created_at
                })
        return files_info

    async def download_file(self, db: AsyncSession, file_id: int, user: User) -> Tuple[bytes, str]:
        """Download and decrypt a file."""
        file_entry = await self.db_ops.GetFileEntry(db, user.id, file_id)
        
        if not file_entry:
            raise FileError
        
        filename = file_entry.filename
        filepath = file_entry.filepath
        original_filename = file_entry.original_filename
        download_filename = original_filename if original_filename else filename
        
        path = filepath.replace('/', os.sep)
        if not os.path.exists(path):
            raise FileError
        
        try:
            user_key = FileService._get_user_key(user)
            decrypted_b64 = self.encryption_service.decrypt(
                filename,
                str(user.id),
                user_key
            )
            decrypted_data = base64.b64decode(decrypted_b64)
            return decrypted_data, download_filename
        except EncryptionServiceError:
            raise EncryptionServiceError

    async def delete_file(self, db: AsyncSession, file_id: int, user: User) -> dict:
        """Delete a file from filesystem and database."""
        file_entry = await self.db_ops.GetFileEntry(db, user.id, file_id)
        
        if not file_entry:
            raise FileError
        
        filepath = file_entry.filepath
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                raise FileError
        
        await self.db_ops.remove_file(db, user.id, file_id)
        return {'message': 'File deleted successfully'}
    

    async def get_dashboard_data(self, db: AsyncSession, user: User) -> List[dict]:
        files = await self.db_ops.GetUserFileByUserid(db, str(user.id))
        return [{
            'id': f.id,
            'filename': f.original_filename or f.filename,
            'created_at': f.created_at.isoformat() if f.created_at else None
        } for f in files]