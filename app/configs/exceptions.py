from fastapi import Request
from fastapi.responses import JSONResponse


class BaseAPIException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, data=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(message)


class NotFoundException(BaseAPIException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            code="NOT_FOUND",
            message=f"ບໍ່ພົບມີ{resource}",
            status_code=404
        )


class ConflictException(BaseAPIException):
    def __init__(self, message: str = "Resource already exists", data=None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            data=data,
        )


class ValidationException(BaseAPIException):
    def __init__(self, message: str = "Invalid data"):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422
        )


class UnauthorizedException(BaseAPIException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401
        )


class ForeignKeyConstraintException(BaseAPIException):
    def __init__(self, message: str = "Cannot delete due to foreign key constraint"):
        super().__init__(
            code="FOREIGN_KEY_CONSTRAINT",
            message=message,
            status_code=400
        )


async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "messages": exc.message,
            "data": exc.data,
        },
    )
