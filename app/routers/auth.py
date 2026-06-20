from app.dependencies import get_user_service, get_jwt_handler
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.user import User
from app.schemas.User import UserLogin, ChangePassword, UserSignup, UserSignupResponse, UserSignOnResponse

from app.services.user_service import UserService


router = APIRouter(prefix="/auth")

@router.post('/signup', response_model=UserSignupResponse)
def signup(
    user: UserSignup,
    userservice: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)):
    return userservice.register(db, user)


@router.post('/login', response_model=UserSignOnResponse)
def login(
    user_data: UserLogin,
    userservice: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)):
    return userservice.login(db, user_data)
   

@router.post('/logout')
def logout():
    return {"message": "Success"}

@router.post('/change-password')
def change_password(
    user_password: ChangePassword,
    userservice: UserService = Depends(get_user_service),
    db: Session = Depends(get_db),
    user: User = Depends(get_jwt_handler.get_current_user)):

    return userservice.change_password(db, user, user_password)