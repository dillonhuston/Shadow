from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import get_db
from app.models.user import User
from app.authservice.jwt_handler import JWTHandler
from app.services.file_service import FileService
from app.exceptions.exceptions import ServiceError, FileError
from app.config import Config 

router = APIRouter(prefix="/file", tags=["files"])
jwt_handle = JWTHandler()

@router.post('/upload', status_code=201)
async def upload_file(
    file: UploadFile,
    file_service: FileService = Depends(),
    current_user: User = Depends(jwt_handle.get_current_user),
    db: AsyncSession = Depends(get_db)):

    if not file or not file.filename:
        raise ServiceError(status_code=400, detail="No file provided")

    file_data = await file.read()
    return await file_service.upload_file(
        db=db,
        file_data=file_data,
        filename=file.filename,
        user=current_user
    )

@router.get('/files')
async def list_files(
    file_service: FileService = Depends(),
    current_user: User = Depends(jwt_handle.get_current_user),
    db: AsyncSession = Depends(get_db)):

    return {'files': await file_service.list_files(db, current_user)}

@router.get('/download/{file_id}')
async def download_file(
    file_id: int,
    file_service: FileService = Depends(),
    current_user: User = Depends(jwt_handle.get_current_user),
    db: AsyncSession = Depends(get_db)):

    decrypted_data, filename = await file_service.download_file(
        db=db,
        file_id=file_id,
        user=current_user
    )
    
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'txt'
    
    return StreamingResponse(
        iter([decrypted_data]),
        media_type=Config.MIMETYPES.get(ext, 'application/octet-stream'),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.delete('/delete/{file_id}')
async def delete_file(
    file_id: int,
    file_service: FileService = Depends(),
    current_user: User = Depends(jwt_handle.get_current_user),
    db: AsyncSession = Depends(get_db)):
    
    return await file_service.delete_file(db, file_id, current_user)