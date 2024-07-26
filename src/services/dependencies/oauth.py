from typing import Awaitable, Callable, Type

from domains.controllers import UserController
from domains.dto import AbstractDTO, UserDTO
from domains.permissions import AbstractObjectPermission, get_permission_table
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from services.dependencies.base import inject_jwt_service
from services.dependencies.controllers import get_user_controller
from services.errors import PermissionDeniedError
from services.security import JwtAuthService
from services.security.oauth import CustomHTTPBearer


def add_auth_user_id_to_request(
        request: Request,
        oauth_creds: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
        oauth_service: JwtAuthService = Depends(inject_jwt_service),

) -> str:
    user_payload = oauth_service.decode_jwt_token(
        oauth_creds.credentials
    )
    request.state.user_id = user_payload.get("sub")
    return request.state.user_id


async def get_current_active_user(
        request: Request,
        user_controller: UserController = Depends(get_user_controller)
) -> UserDTO:
    return await user_controller.get(request.state.user_id)


def check_object_permission(
        operation: str,
        user: UserDTO,
        item: AbstractDTO,
) -> bool:
    permission_table = get_permission_table()
    object_permission_class: Type[AbstractObjectPermission] = permission_table.get(item.__repr_name__)
    object_permission = object_permission_class.get_object_lvl_permission(item)
    for permission in object_permission:
        if operation == permission[0]:
            allowed_roles = permission[1]
            return "all" in allowed_roles or user.role in allowed_roles or user.id in allowed_roles
    return False


def check_operation_permission(
        operation: str,
        user: UserDTO,
):
    model_name = operation.split(":")[0]
    permission_table = get_permission_table()
    object_permission_class: Type[AbstractObjectPermission] = permission_table.get(model_name)
    operation_permission = object_permission_class.get_operation_lvl_permission()
    for permission in operation_permission:
        if operation == permission[0]:
            allowed_roles = permission[1]
            if "all" in allowed_roles or user.role.value in allowed_roles:
                return
    raise PermissionDeniedError


def check_route_permission(
        operation: str,
):
    def wrapper(func: Callable[..., Awaitable]):
        async def inner(*args, **kwargs):
            user = await get_current_active_user(kwargs.get("request"))
            check_operation_permission(operation, user)
            return await func(*args, **kwargs)

        return inner

    return wrapper
