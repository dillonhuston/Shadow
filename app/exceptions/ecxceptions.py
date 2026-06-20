class ServiceError(Exception):
    pass

class UserAlreadyExistsError(ServiceError):
    pass

class AuthenticationError(ServiceError):
    pass

class IncorrectPasswordError(ServiceError):
    pass