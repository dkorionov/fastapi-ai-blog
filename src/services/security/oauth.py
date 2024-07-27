from datetime import datetime, timedelta, timezone
from typing import Literal, Type

import jwt
from core.config import SecuritySettings
from domains.dto import AbstractDTO, UserDTO
from domains.permissions import AbstractObjectPermission, get_permission_table
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from starlette.requests import Request

from services.errors.oauth import (
    InvalidTokenTypeError,
    PermissionDeniedError,
    UnauthorizedError,
)


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials) and self.auto_error:
            raise UnauthorizedError
        if scheme.lower() != "bearer" and self.auto_error:
            raise UnauthorizedError
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class JwtAuthService:
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, security_settings: SecuritySettings):
        self._security_settings = security_settings

    def _generate_token_payload(self, user_id: int, token_type: str) -> dict[str, str]:
        lifetime = self._security_settings.ACCESS_TOKEN_EXPIRES_MINUTES
        return {
            "exp": (datetime.now(timezone.utc) + timedelta(minutes=lifetime)).timestamp(),
            "iat": datetime.now(timezone.utc).timestamp(),
            "sub": user_id,
            "type": token_type,
        }

    def generate_jwt_tokens(self, user_id: int) -> dict[str, str]:
        access_payload = self._generate_token_payload(user_id, token_type="access")
        refresh_payload = self._generate_token_payload(user_id, token_type="refresh")
        return {
            "access_token": jwt.encode(
                access_payload,
                key=self._security_settings.SECRET_KEY,
                algorithm=self._security_settings.ALGORITHM
            ),
            "access_token_expires_at": str(access_payload["exp"]),
            "refresh_token": jwt.encode(
                refresh_payload,
                key=self._security_settings.SECRET_KEY,
                algorithm=self._security_settings.ALGORITHM
            ),
            "refresh_token_expires_at": str(refresh_payload["exp"]),
        }

    def refresh_token(self, refresh_token: str) -> (dict[str, str], int):
        payload = self.decode_jwt_token(refresh_token)
        if payload["type"] != "refresh":
            raise InvalidTokenTypeError
        return self.generate_jwt_tokens(int(payload["sub"])), payload["sub"]

    def decode_jwt_token(self, token: str) -> dict[str, str]:
        try:
            payload = jwt.decode(
                token,
                key=self._security_settings.SECRET_KEY,
                algorithms=[self._security_settings.ALGORITHM]
            )
            if payload["type"] == Literal["access", "refresh"]:
                raise InvalidTokenTypeError
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenTypeError

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self._pwd_context.hash(password)


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
