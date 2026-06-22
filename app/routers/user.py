from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.models.db import get_db
from sqlalchemy.orm import Session
from app.services.file_service import FileService

from app.authservice.jwt_handler import JWTHandler
router = APIRouter(prefix="/user")

@router.get('/dashboard')
def dashboard(
    file_service: FileService = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(JWTHandler().get_current_user)):
    
    try:
        files = file_service.get_dashboard_data(db, current_user)
        return {'files': files}
    except Exception:
        raise HTTPException(status_code=500, detail="Dashboard load failed")