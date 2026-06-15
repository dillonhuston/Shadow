import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.user import User
from app.schemas.User import UserLogin, UserSignup, UserSignupResponse, UserSignOnResponse

from app.authservice.auth import (
    add_user, 
    get_user_by_username, 
    authenticate_user, 
    generate_web_token, 
    verify_password, 
    get_password_hash
)
from app.authservice.jwt_handler import get_current_user

router = APIRouter(prefix="/auth")

@router.post('/signup', response_model=UserSignupResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = add_user(db, user)
    return {
        "id": str(new_user.id),
        "email": new_user.email
    }

@router.post('/login', response_model=UserSignOnResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    token = generate_web_token({
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
    current_user: User = Depends(get_current_user)):

    # Make sure password is strong
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$', new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter and one number")
    
    # Check current password
    if not verify_password(current_password, str(current_user.password)):
        raise HTTPException(status_code=400, detail="Current password incorrect")
        
    current_user.password = get_password_hash(new_password)# type: ignore
    db.commit()
    
    return {"message": "Password changed successfully"}