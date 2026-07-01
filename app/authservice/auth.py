import os 
import jwt
from typing import Optional

from datetime import datetime, timezone, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

class AuthService():
    def __init__(self)-> None:
        #TODO Move to config.py

        self.SECRETKEY = os.getenv("SECRET_KEY")
        self.ALGORTHIM = os.getenv("ALGROITHM")
        self.ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self,plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password[:72], hashed_password)

    
    def get_password_hash(self, password: str)-> str:
        return self.pwd_context.hash(password[:72])
    

    def generate_web_token(self,data: dict)-> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRETKEY, algorithm=self.ALGORTHIM)
    

    def verify_web_token(self, token: str)-> Optional[dict]:
        try:
            payload = jwt.decode(token, self.SECRETKEY, algorithms=self.ALGORTHIM)
            return payload
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None