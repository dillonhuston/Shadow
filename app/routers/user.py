from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.models.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.file_service import FileService

from app.authservice.jwt_handler import JWTHandler
router = APIRouter(prefix="/user")

@router.get('/dashboard')
async def dashboard(
    file_service: FileService = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(JWTHandler().get_current_user)):
    
    return {'files': await file_service.get_dashboard_data(db, current_user)}