import re
from  app.dependencies import get_user_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db

from app.models.user import User
from app.schemas.User import UserLogin, UserSignup, UserSignupResponse, UserSignOnResponse

from app.authservice.jwt_handler import JWTHandler
from app.authservice.auth import AuthService
from app.authservice.user import AuthUserFuncs

from app.services.user_service import UserService


#TODO remove this and add DI
jwt_handle = JWTHandler()
auth_service = AuthService()
user_auth_funcs = AuthUserFuncs()

router = APIRouter(prefix="/auth")

@router.post('/signup', response_model=UserSignupResponse)
def signup(
    user: UserSignup,
    userservice: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)):
    return userservice.register(db, user)



@router.post('/login', response_model=UserSignOnResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = user_auth_funcs.authenticate_user(db, user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    token = auth_service.generate_web_token({
        "sub": user.username,
        "id": str(user.id)}
    )
    return {
        "id": str(user.id),
        "email": user.email,
        "access_token": token,
        "token_type": "bearer"
    }

@router.post('/logout')
def logout():
    return {"message": "Success"}

@router.post('/change-password')
def change_password(
    current_password: str, 
    new_password: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_handle.get_current_user)):

    # Make sure password is strong
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$', new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter and one number")
    
    # Check current password
    if not user_auth_funcs.verify_password(current_password, str(current_user.password)):
        raise HTTPException(status_code=400, detail="Current password incorrect")
        
    current_user.password = auth_service.get_password_hash(new_password)
    
    return {"message": "Password changed successfully"}