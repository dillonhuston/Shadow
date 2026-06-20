import uuid
import os

from app.exceptions.ecxceptions import UserAlreadyExistsError, AuthenticationError
from app.schemas.User import UserSignup, UserLogin
from app.models.user import User
from sqlalchemy.orm import Session
from app.DatabaseOps.DatabaseRespitory import DatabaseOps
from app.authservice.auth import AuthService
from app.authservice.jwt_handler import JWTHandler


class UserService():

    def __init__(self, dbops: DatabaseOps, auth: AuthService, jwt_handle: JWTHandler) -> None:
        self.db_ops = dbops
        self.auth = auth

        
    def register(self, db:Session, user: UserSignup):
        if self.db_ops.GetUserByusername(db, user.username):
            raise UserAlreadyExistsError()
        
        hashed_password = self.auth.get_password_hash(user.password)

        new_user = User(
            id = str(uuid.uuid4()),
            username = user.username,
            email = user.email,
            password = hashed_password,
            key = os.urandom(16).hex() # this should not be happening here, i will get this implemented soon
        )
        return self.db_ops.add(db, new_user)


    def login(self, db: Session, user_login: UserLogin):
        user = self.db_ops.GetUserByusername(db, user_login.username)
        if not user or not self.auth.verify_password(user_login.password,user.password):
            raise AuthenticationError()
        
        payload = {
            "sub": user.username,
            "id": str(user.id)
        }
        
        token = self.auth.generate_web_token(payload)
        
        return{
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "access_token": token,
            "token_type": "bearer"
        }
   


