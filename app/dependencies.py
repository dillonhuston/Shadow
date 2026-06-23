from app.DatabaseOps.DatabaseRepository import DatabaseOps
from app.authservice.auth import AuthService
from app.services.user_service import UserService
from app.authservice.jwt_handler import JWTHandler


def get_user_service() -> UserService:
    repo = DatabaseOps()
    auth = AuthService()
    jwt_handle = JWTHandler()
    return UserService(repo, auth, jwt_handle)

def get_jwt_handler() -> JWTHandler:
    return JWTHandler()