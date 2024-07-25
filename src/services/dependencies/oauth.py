from core.config.constansts import UserRole
from domains.controllers import UserController
from domains.dto import UserDTO
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


def has_permission(roles: list[UserRole]):
    async def permission_checker(user: UserDTO = Depends(get_current_active_user)) -> bool:
        if user.role not in roles:
            raise PermissionDeniedError
        return True

    return permission_checker
