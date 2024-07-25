import pytest
from domains.controllers import OauthController, UserController
from services.schemas.oauth import RegisterSchema

from tests.factories import UserFactory


class TestAuthController:
    @pytest.mark.anyio
    async def test_login(
            self,
            provide_user_controller: UserController,
            provide_auth_controller: OauthController,
    ):
        user = UserFactory(id=None)
        await provide_user_controller.create(user)
        response, tokens = await provide_auth_controller.login(user.username, user.password)
        assert response.username == user.username
        assert response.email == user.email
        assert tokens["access_token"]
        assert tokens["refresh_token"]

    @pytest.mark.anyio
    async def test_register(
            self,
            provide_auth_controller: OauthController,
    ):
        user_to_register = UserFactory(id=None)
        user_data = RegisterSchema(
            username=user_to_register.username,
            email=user_to_register.email,
            password=user_to_register.password,
        )
        registered_user, tokens = await provide_auth_controller.register(user_data.model_dump())
        assert registered_user.username == user_to_register.username
        assert registered_user.email == user_to_register.email
        assert tokens["access_token"]
        assert tokens["refresh_token"]
        assert provide_auth_controller.jwt_service.verify_password(
            user_to_register.password,
            registered_user.password
        )

    @pytest.mark.anyio
    async def test_refresh_token(
            self,
            provide_user_controller: UserController,
            provide_auth_controller: OauthController,
    ):
        user = UserFactory(id=None)
        await provide_user_controller.create(user)
        oauth_user, tokens = await provide_auth_controller.login(user.username, user.password)
        _, new_tokens = await provide_auth_controller.refresh_access_token(tokens["refresh_token"])
        assert tokens["access_token"] != new_tokens["access_token"]
        assert tokens["refresh_token"] != new_tokens["refresh_token"]
        assert oauth_user.username == user.username
        assert oauth_user.email == user.email
