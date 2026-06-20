class ServiceError(Exception):
    pass

class UserAlreadyExistsError(ServiceError):
    pass