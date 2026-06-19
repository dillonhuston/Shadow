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


    def get_user_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def verify_password(self,plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password[:72], hashed_password)

    def authenticate_user(self, db: Session, username: str, password: str):
        user = self.get_user_by_username(db, username)
        if not user or not self.verify_password(password, str(user.password)):
            return None
        return user

    def add_user(self, db: Session, user_data: UserSignup):
        if self.get_user_by_username(db, user_data.username):
            raise HTTPException(status_code=400, detail="Username already registered.")
            
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        new_user = User(
            id = str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            key=os.urandom(16).hex()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    