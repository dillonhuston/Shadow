import uuid
import os

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.User import UserSignup
from passlib.context import CryptContext 
from fastapi import HTTPException
from app.authservice.auth import AuthService


auth_service = AuthService()


class AuthUserFuncs():

    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



   