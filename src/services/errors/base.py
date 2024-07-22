from abc import ABCMeta

from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorModel(BaseModel):
    ok: bool = False
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error: str = "Internal Server Error"
    detail: str | None = None


class AbstractError(Exception, metaclass=ABCMeta):
    error = "Internal Server Error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "An error occurred"

    def __init__(
            self,
            *,
            detail: str | None = None,
            headers: dict[str, str] | None = None,
            status_code: int | None = None,
    ) -> None:
        self.detail = detail or self.error
        self.headers = headers
        self.status_code = status_code or self.status_code


class ResourceNotFoundError(AbstractError):
    error = "Resource Not Found"
    status_code = 404

    def __init__(self, *, detail: str | None = None) -> None:
        super().__init__(detail=detail)


async def global_exception_handler(request: Request, exc: AbstractError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorModel(
            error=exc.error,
            detail=exc.detail,
            status_code=exc.status_code,
        ).model_dump(),
    )
