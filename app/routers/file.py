import os
import base64

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.user import User
from app.authservice.jwt_handler import JWTHandler
from app.services.file_service import FileService
from app.services.encryption import EncryptionError
from app.config import Config 

router = APIRouter(prefix="/file", tags=["files"])
jwt_handle = JWTHandler()

@router.post('/upload', status_code=201)
async def upload_file(
    file: UploadFile,
    file_service: FileService,
    current_user: User = Depends(jwt_handle.get_current_user),
    db: Session = Depends(get_db)):

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    try:
        file_data = await file.read()
        result = file_service.upload_file(
            db=db,
            file_data=file_data,
            filename=file.filename,
            user=current_user
        )
        return result

    except EncryptionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get('/files')
def list_files(
    file_service: FileService,
    current_user: User = Depends(jwt_handle.get_current_user),
    db: Session = Depends(get_db)):

    try:
        files = file_service.list_files(db, current_user)
        return {'files': files}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.get('/download/{file_id}')
async def download_file(
    file_id: int,
    file_service: FileService,
    current_user: User = Depends(jwt_handle.get_current_user),
    db: Session = Depends(get_db)):

    try:
        decrypted_data, filename = file_service.download_file(
            db=db,
            file_id=file_id,
            user=current_user
        )
        
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'txt'
        
        return StreamingResponse(
            iter([decrypted_data]),
            media_type=Config.MIMETYPES.get(ext, 'application/octet-stream'),
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Download failed")


@router.delete('/delete/{file_id}')
def delete_file(
    file_id: int,
    file_service: FileService,
    current_user: User = Depends(jwt_handle.get_current_user),
    db: Session = Depends(get_db)):
    
    try:
        result = file_service.delete_file(db, file_id, current_user)
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete file")