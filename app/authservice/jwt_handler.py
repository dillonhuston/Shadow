import jwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jwt.exceptions import PyJWTError 
from app.models.db import get_db
from app.models.user import User
from app.authservice.user import AuthUserFuncs
from dotenv import load_dotenv

load_dotenv()
auth_service = AuthUserFuncs()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class JWTHandler():
    def __init__(self) -> None:
        self.SECRETKEY = os.getenv("SECRET_KEY")
        self.ALGORTHIM = os.getenv("ALGORITHM", "HS256")
        
        
    def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.SECRETKEY, algorithms=self.ALGORTHIM)
            username = payload.get("sub")
            
            if not isinstance(username, str):
                raise credentials_exception
                
        except PyJWTError as e:
            print(f"[JWT] Decode error: {e}")  # Debug logging
            raise credentials_exception
        
        user = auth_service.get_user_by_username(db, username)
        
        if user is None:
            raise credentials_exception
            
        return user