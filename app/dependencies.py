from app.DatabaseOps.DatabaseRespitory import DatabaseOps
from app.authservice.auth import AuthService
from app.services.user_service import UserService
from app.authservice.jwt_handler import JWTHandler

from app.models.db import get_db

def get_user_service() -> UserService:
    repo = DatabaseOps()
    auth = AuthService()
    jwt_handle = JWTHandler()
    return UserService(repo, auth, jwt_handle)
