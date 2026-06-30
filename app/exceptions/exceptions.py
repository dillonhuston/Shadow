from fastapi import status

class ServiceError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred."

class UserAlreadyExistsError(ServiceError):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists."

class AuthenticationError(ServiceError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication failed."

class IncorrectPasswordError(ServiceError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect password."


class FileError(ServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "File operation failed."

class EncryptionServiceError(ServiceError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Encryption error."

class DatabaseError(ServiceError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Database error."

class DashboardError(ServiceError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Dashboard error."