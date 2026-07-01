from fastapi import status
from typing import Optional
class ServiceError(Exception):
    """Base class for all service-related errors."""
    def __init__(self, detail:  Optional[str] = None, status_code: Optional[int]=None):
        self.detail = detail or "An unexpected error occurred."
        self.status_code = status_code or status.HTTP_500_INTERNAL_SERVER_ERROR

class UserAlreadyExistsError(ServiceError):
    def __init__(self, detail: str = "User already exists."):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class AuthenticationError(ServiceError):
    def __init__(self, detail: str = "Authentication failed."):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class IncorrectPasswordError(ServiceError):
    def __init__(self, detail: str = "Incorrect password."):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class FileError(ServiceError):
    def __init__(self, detail: str = "File operation failed."):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class EncryptionServiceError(ServiceError):
    def __init__(self, detail: str = "Encryption error."):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DatabaseError(ServiceError):
    def __init__(self, detail: str = "Database error."):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardError(ServiceError):
    def __init__(self, detail: str = "Dashboard error."):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)