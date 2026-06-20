from app.DatabaseOps.DatabaseRespitory import DatabaseOps
from app.authservice.auth import AuthService
from services.user_service import UserService

def get_user_service() -> UserService:

    repo = DatabaseOps()
    auth = AuthService()
    return UserService(repo, auth)
