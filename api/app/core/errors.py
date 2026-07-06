class AppError(Exception):
    status_code = 500
    code = "APP_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BadRequestAppError(AppError):
    status_code = 400
    code = "BAD_REQUEST"


class ValidationAppError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class NotFoundAppError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictAppError(AppError):
    status_code = 409
    code = "CONFLICT"


class DatabaseAppError(AppError):
    status_code = 500
    code = "DATABASE_ERROR"
