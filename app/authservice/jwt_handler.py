import jwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jwt.exceptions import PyJWTError 
from app.models.db import get_db
from app.models.user import User
from app.authservice.auth import get_user_by_username
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Use environment variables with fallbacks
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not isinstance(username, str):
            raise credentials_exception
            
    except PyJWTError as e:
        print(f"[JWT] Decode error: {e}")  # Debug logging
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    
    if user is None:
        raise credentials_exception
        
    return user