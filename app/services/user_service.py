import uuid
import os

from app.exceptions.ecxceptions import UserAlreadyExistsError
from app.schemas.User import UserSignup
from app.models.user import User
from sqlalchemy.orm import Session
from app.DatabaseOps.DatabaseRespitory import DatabaseOps
from app.authservice.auth import AuthService

class UserService():

    def __init__(self, dbops: DatabaseOps, auth: AuthService) -> None:
        self.Databaseops = dbops
        self.auth = auth
        


    def register(self, db:Session, user: UserSignup):
        if self.Databaseops.GetUserByusername(db, user.username):
            raise UserAlreadyExistsError()
        
        hashed_password = self.auth.get_password_hash(user.password)


        new_user = User(
            id = str(uuid.uuid4()),
            username = user.username,
            email = user.email,
            password = hashed_password,
            key = os.urandom(16).hex() # this should not be happening here, i will get this implemented soon
        )

        self.Databaseops.add(db, new_user)
   


