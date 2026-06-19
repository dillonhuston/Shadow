import os
import base64
from typing import List, Tuple, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.models.file import File as FileModel
from app.models.user import User
from app.config import Config
from app.services.encryption import EncryptionService, EncryptionError

encryption_service = EncryptionService()
class FileService:

    @staticmethod
    def _get_user_key(user: User) -> str:
        """Safely extract user's key as string."""
        return str(user.key) if user.key is not None else ""
    
    @staticmethod
    def _safe_str(value) -> Optional[str]:
        """Safely convert SQLAlchemy column to string or None."""
        if value is None:
            return None
        return str(value)
    
    @staticmethod
    def _safe_str_or_empty(value) -> str:
        """Safely convert SQLAlchemy column to string, empty string if None."""
        if value is None:
            return ""
        return str(value)
    
    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """Safely convert SQLAlchemy column to int or None."""
        if value is None:
            return None
        return int(str(value)) 
    
    @staticmethod
    def upload_file(db: Session, file_data: bytes, filename: str, user: User) -> dict:
        """Handle file upload, encryption, and database storage."""
        try:
            # Sanitize filename
            safe_filename = secure_filename(filename)
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            # Get user key as string
            user_key = FileService._get_user_key(user)
            
            # Encrypt the file
            encrypted_filename = encryption_service.encrypt(
                encoded_data,
                safe_filename,
                str(user.id),
                user_key
            )
            
            encrypted_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)
            
            # Create database entry
            new_file = FileModel(
                user_id=str(user.id),
                filename=encrypted_filename,
                filepath=encrypted_path,
                original_filename=safe_filename
            )
            
            db.add(new_file)
            db.commit()
            db.refresh(new_file)
            
            return {'message': f'{safe_filename} uploaded'}
            
        except EncryptionError as e:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def list_files(db: Session, user: User) -> List[dict]:
        """List all files for a user."""
        files_info: List[dict] = []
        
        # Get user's files from database
        user_files = db.query(FileModel).filter_by(user_id=str(user.id)).all()
        
        for file_entry in user_files:
            filepath = FileService._safe_str_or_empty(file_entry.filepath)
            if os.path.exists(filepath):
                # Safely convert all values
                original_filename = FileService._safe_str(file_entry.original_filename)
                filename = original_filename if original_filename else FileService._safe_str_or_empty(file_entry.filename)
                created_at = file_entry.created_at.isoformat() if file_entry.created_at is not None else None
                
                # Convert id to int safely
                file_id = FileService._safe_int(file_entry.id)
                
                files_info.append({
                    'id': file_id,  # Now file_id is int or None
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'created_at': created_at
                })
        
        return files_info
    
    @staticmethod
    def download_file(db: Session, file_id: int, user: User) -> Tuple[bytes, str]:
        """Download and decrypt a file."""
        # Get file entry from database
        file_entry = db.query(FileModel).filter_by(
            id=file_id,
            user_id=str(user.id)
        ).first()
        
        if not file_entry:
            raise HTTPException(
                status_code=404,
                detail="File not found or unauthorized"
            )
        
        # Get file details - use helper methods
        filename = FileService._safe_str_or_empty(file_entry.filename)
        filepath = FileService._safe_str_or_empty(file_entry.filepath)
        original_filename = FileService._safe_str(file_entry.original_filename)
        download_filename = original_filename if original_filename else filename
        
        # Check if file exists on filesystem
        path = filepath.replace('/', os.sep)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="File not found on server")
        
        try:
            # Get user key as string
            user_key = FileService._get_user_key(user)
            
            # Decrypt the file
            decrypted_b64 = encryption_service.decrypt(
                filename,
                str(user.id),
                user_key
            )
            decrypted_data = base64.b64decode(decrypted_b64)
            
            return decrypted_data, download_filename
            
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
        except Exception as e:
            raise
    
    @staticmethod
    def delete_file(db: Session, file_id: int, user: User) -> dict:
        """Delete a file from filesystem and database."""
        # Get file entry from database
        file_entry = db.query(FileModel).filter_by(
            id=file_id,
            user_id=str(user.id)
        ).first()
        
        if not file_entry:
            raise HTTPException(
                status_code=404,
                detail="File not found or unauthorized"
            )
        
        # Get file details - use helper methods
        filename = FileService._safe_str_or_empty(file_entry.filename)
        filepath = FileService._safe_str_or_empty(file_entry.filepath)
        
        # Delete from filesystem
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError as e:
                raise HTTPException(status_code=500, detail="Failed to delete file from server")
        
        # Delete from database
        db.delete(file_entry)
        db.commit()
        
        return {'message': 'File deleted successfully'}