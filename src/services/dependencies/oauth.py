from core.config import MainSettings, create_settings
from core.config.constansts import UserRole
from domains.controllers import OauthController
from domains.providers.oauth import provide_oauth_controller
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from services.dependencies.base import inject_database, inject_jwt_service
from services.dependencies.users import get_current_active_user
from services.errors import PermissionDeniedError
from services.schemas.user import BaseUser
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


def get_oauth_controller(
        settings: MainSettings = Depends(create_settings)
) -> OauthController:
    return provide_oauth_controller(
        db=inject_database(settings=settings),
        jwt_service=inject_jwt_service(settings=settings)
    )


def has_permission(roles: list[UserRole]):
    async def permission_checker(user: BaseUser = Depends(get_current_active_user)) -> bool:
        if user.role not in roles:
            raise PermissionDeniedError
        return True

    return permission_checker
