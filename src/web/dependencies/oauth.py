from typing import Awaitable, Callable

from db import Database
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from services.oauth import CustomHTTPBearer, JwtAuthService
from services.permissions import check_operation_permission
from services.repositories.users import UserRepository

from web.dependencies.base import inject_database, inject_jwt_service


async def add_auth_user_to_request(
        request: Request,
        oauth_creds: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
        oauth_service: JwtAuthService = Depends(inject_jwt_service),
        db: Database = Depends(inject_database),

) -> str:
    user_payload = oauth_service.decode_jwt_token(
        oauth_creds.credentials
    )
    async with db.get_async_session() as session:
        repository = UserRepository()
        user = await repository.get(session, int(user_payload.get("sub")))
    request.state.user = user
    return user


def check_route_permission(
        operation: str,
):
    def wrapper(func: Callable[..., Awaitable]):
        async def inner(*args, **kwargs):
            print("HERE")
            user = kwargs["request"].state.user
            check_operation_permission(operation, user)
            return await func(*args, **kwargs)

        return inner

    return wrapper
