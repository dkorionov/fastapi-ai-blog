from fastapi import status

from .base import AbstractError


class InvalidCredentialsError(AbstractError):
    error = "Invalid Credentials"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class InvalidTokenTypeError(AbstractError):
    error = "Invalid Token Type"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class ExpiredTokenError(AbstractError):
    error = "Expired Token"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class UnauthorizedError(AbstractError):
    error = "Unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class PermissionDeniedError(AbstractError):
    error = "Permission Denied"
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, *, detail: str | None = None) -> None:
        super().__init__(detail=detail)
