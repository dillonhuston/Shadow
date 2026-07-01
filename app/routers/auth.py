from app.dependencies import get_user_service, get_jwt_handler
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import get_db
from app.models.user import User
from app.schemas.User import UserLogin, ChangePassword, UserSignup, UserSignupResponse, UserSignOnResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth")

@router.post('/signup', response_model=UserSignupResponse)
async def signup(
    user: UserSignup,
    userservice: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db)):
    return await userservice.register(db, user)


@router.post('/login', response_model=UserSignOnResponse)
async def login(
    user_data: UserLogin,
    userservice: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db)):
    return await userservice.login(db, user_data)
   
# this need to actualy logout
@router.post('/logout')
async def logout():
    return {"message": "Success"}

@router.post('/change-password')
async def change_password(
    user_password: ChangePassword,
    userservice: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_jwt_handler.get_current_user)):

    return await userservice.change_password(db, user, user_password)