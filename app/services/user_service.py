import uuid
import os
import re

from app.exceptions.exceptions import UserAlreadyExistsError, AuthenticationError, IncorrectPasswordError 
from app.schemas.User import UserSignup, UserLogin, ChangePassword

from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.DatabaseOps.DatabaseRepository import DatabaseOps
from app.authservice.auth import AuthService
from app.authservice.jwt_handler import JWTHandler


class UserService():

    def __init__(self, dbops: DatabaseOps, auth: AuthService, jwt_handle: JWTHandler ) -> None:
        self.db_ops = dbops
        self.auth = auth

        
    async def register(self, db: AsyncSession, user: UserSignup):
        if await self.db_ops.GetUserByusername(db, user.username):
            raise UserAlreadyExistsError()
        
        hashed_password = self.auth.get_password_hash(user.password)

        new_user = User(
            id = str(uuid.uuid4()),
            username = user.username,
            email = user.email,
            password = hashed_password,
            key = os.urandom(16).hex() # this should not be happening here, i will get this implemented soon
        )
        return await self.db_ops.add(db, new_user)


    async def login(self, db: AsyncSession, user_login: UserLogin):
        user = await self.db_ops.GetUserByusername(db, user_login.username)
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
    
    async def change_password(self, db: AsyncSession, user: User, password_data: ChangePassword):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$',password_data.new_password):
            raise IncorrectPasswordError
        
        if not self.auth.verify_password(password_data.current_password, str(user.password)):
            raise IncorrectPasswordError
        user.password = self.auth.get_password_hash(password_data.new_password)
        await db.commit() #TODO remove this
        return{"message": "Pasword changed"}
        
