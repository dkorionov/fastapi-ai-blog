from domains.controllers.oauth import OauthController
from fastapi import APIRouter, Depends, status
from services.dependencies.oauth import get_oauth_controller
from services.schemas.oauth import (
    LoginSchema,
    RefreshTokenInputSchema,
    RegisterSchema,
    ResponseTokenScheme,
)

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
        oauth_controller: OauthController = Depends(get_oauth_controller)
) -> ResponseTokenScheme:
    return await oauth_controller.login(data.username, data.password)


@router.post(
    "/register",
    name=register_url_name,
    response_model=ResponseTokenScheme,
    status_code=status.HTTP_201_CREATED
)
async def register(
        data: RegisterSchema,
        oauth_controller: OauthController = Depends(get_oauth_controller)
) -> ResponseTokenScheme:
    return await oauth_controller.register(data)


@router.post(
    "/refresh-token",
    name=refresh_token_url_name,
    response_model=ResponseTokenScheme,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
        refresh_token_data: RefreshTokenInputSchema,
        oauth_controller: OauthController = Depends(get_oauth_controller)
) -> ResponseTokenScheme:
    return await oauth_controller.refresh_access_token(refresh_token_data.refresh_token)
