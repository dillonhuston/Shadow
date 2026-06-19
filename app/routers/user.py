from fastapi import APIRouter, Depends
from app.authservice.jwt_handler import JWTHandler
from app.models.user import User
from app.models.file import File 
from app.models.db import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user")
jwt_handle = JWTHandler()

@router.get('/dashboard')
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_handle.get_current_user)):

    files = db.query(File).filter(File.user_id == current_user.id).all()
    return {
        'files': [{
            'id': f.id,
            'filename': f.original_filename or f.filename,
            'created_at': f.created_at.isoformat()
        } for f in files]
    }