from db import Database
from db.models import UserModel
from fastapi import APIRouter, Depends, status
from schemas.oauth import (
    LoginSchema,
    RefreshTokenInputSchema,
    RegisterSchema,
    ResponseTokenScheme,
)
from schemas.users import OutputUserSchema
from services.errors import InvalidCredentialsError
from services.oauth import JwtAuthService
from services.repositories.users import UserRepository

from web.dependencies import inject_database, inject_jwt_service

router = APIRouter()

login_url_name = "login"
register_url_name = "register"
refresh_token_url_name = "refresh-token"


@router.post(
    "/login",
    name=login_url_name,
    response_model=ResponseTokenScheme,
    status_code=status.HTTP_200_OK
)
async def login(
        data: LoginSchema,
        jwt_service: JwtAuthService = Depends(inject_jwt_service),
        db: Database = Depends(inject_database),
        repository: UserRepository = Depends(UserRepository)

) -> ResponseTokenScheme:
    async with db.get_async_session() as session:
        user = await repository.get_by_username(session, data.username)
    if not jwt_service.verify_password(data.password, user.password):
        raise InvalidCredentialsError
    tokens = jwt_service.generate_jwt_tokens(user.id)
    return ResponseTokenScheme(
        **OutputUserSchema.model_validate(user, from_attributes=True).model_dump(),
        **tokens
    )


@router.post(
    "/register",
    name=register_url_name,
    response_model=ResponseTokenScheme,
    status_code=status.HTTP_201_CREATED
)
async def register(
        data: RegisterSchema,
        jwt_service: JwtAuthService = Depends(inject_jwt_service),
        db: Database = Depends(inject_database),
        repository: UserRepository = Depends(UserRepository)
) -> ResponseTokenScheme:
    user = UserModel(**data.model_dump())
    user.password = jwt_service.hash_password(data.password)
    async with db.get_async_session() as session:
        await repository.create_with_settings(session, user)
    tokens = jwt_service.generate_jwt_tokens(user.id)
    return ResponseTokenScheme(
        **OutputUserSchema.model_validate(user, from_attributes=True).model_dump(),
        **tokens
    )


@router.post(
    "/refresh-token",
    name=refresh_token_url_name,
    response_model=ResponseTokenScheme,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
        refresh_token_data: RefreshTokenInputSchema,
        jwt_service: JwtAuthService = Depends(inject_jwt_service),
        db: Database = Depends(inject_database),
        repository: UserRepository = Depends(UserRepository)
) -> ResponseTokenScheme:
    tokens, user_id = jwt_service.refresh_token(refresh_token_data.refresh_token)
    async with db.get_async_session() as session:
        user = await repository.get(session, user_id)
    return ResponseTokenScheme(
        **OutputUserSchema.model_validate(user, from_attributes=True).model_dump(),
        **tokens
    )
