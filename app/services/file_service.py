import os
import base64
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.utils import secure_filename

from pathlib import Path

from app.models.file import File as FileModel
from app.models.user import User
from app.config import Config
from app.services.encryption import EncryptionService
from app.DatabaseOps.DatabaseRepository import DatabaseOps
from app.exceptions.exceptions import FileError, EncryptionServiceError, DatabaseError, DashboardError

#TODO again remove some uselss exceptions, slowly implement custom handler and reponses
class FileService:
    def __init__(self, db_ops: DatabaseOps, encryption_service: EncryptionService) -> None:
        self.db_ops = db_ops
        self.encryption_service = encryption_service

    async def _get_user_key(self,user: User) -> str:
        """Safely extract user's key as string."""
        return str(user.key) if user.key is not None else ""

    async def upload_file(self, db: AsyncSession, file_data: bytes, filename: str, user: User):
        safe_filename = secure_filename(filename)
        user_key = await FileService._get_user_key(self,user)
            
        encrypted_filename = await self.encryption_service.encrypt(
            file_data,
            safe_filename,
            str(user.id),
            user_key
        )
        target_path = Path(Config.ENCRYPTED_FILE_PATH) / encrypted_filename    
        new_file = FileModel(
            user_id=str(user.id),
            filename=encrypted_filename,
            filepath=str(target_path),
            original_filename=safe_filename
        )
        await self.db_ops.add_file(db, new_file)            
        return {'message': f'{safe_filename} uploaded'}

    async def list_files(self, db: AsyncSession, user: User) -> List[dict]:
        files_info: List[dict] = []
        user_files = await self.db_ops.GetUserFileByUserid(db, user_id=user.id)
        
        for entry in user_files:
            path = Path(entry.filepath)
            if path.exists():
               
                files_info.append({
                    'id': entry.id,  
                    'filename': entry.filename,
                    'size': path.stat().st_size,
                    'created_at': entry.created_at
                })
        return files_info

    async def download_file(self, db: AsyncSession, file_id: int, user: User) -> Tuple[bytes, str]:
        """Download and decrypt a file."""
        file_entry = await self.db_ops.GetFileEntry(db, user.id, file_id)
        if not file_entry:
            raise FileError("File is not available or does not exist. ")
        download_filename = file_entry.original_filename if file_entry.original_filename else file_entry.filename
        
        
        path = Path(file_entry.filepath)
        if not path.exists():
            raise FileError(f"File path {file_entry.filepath} does not exist")
        
        try:
            user_key = await self._get_user_key(user)
            decrypted_b64 = await self.encryption_service.decrypt(
                file_entry.filename,
                str(user.id),
                user_key
            )
            return decrypted_b64, download_filename
        except EncryptionServiceError as e:
            raise EncryptionServiceError(f"Failed to download file: {file_entry.original_filename} {e}")

    async def delete_file(self, db: AsyncSession, file_id: int, user: User) -> dict:
        """Delete a file from filesystem and database."""
        file_entry = await self.db_ops.GetFileEntry(db, user.id, file_id)
        
        if not file_entry:
            raise FileError("File entry not found in datbase")
        
        filepath = Path(file_entry.filepath)
        
        if filepath.exists():
                filepath.unlink()        
        await self.db_ops.remove_file(db, user.id, file_id)
        return {'message': 'File deleted successfully'}
    

    async def get_dashboard_data(self, db: AsyncSession, user: User) -> List[dict]:
        files = await self.db_ops.GetUserFileByUserid(db, str(user.id))
        if not files:
            raise DashboardError(f"The dashboard has failed to return the user {user.username} files")
        return [{
            'id': f.id,
            'filename': f.original_filename or f.filename,
            'created_at': f.created_at.isoformat() if f.created_at else None
        } for f in files]