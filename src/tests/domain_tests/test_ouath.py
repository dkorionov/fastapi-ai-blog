import pytest
from domains.controllers import OauthController, UserController
from services.schemas.oauth import RegisterSchema

from tests.factories.user import UserFactory


class TestAuthController:
    @pytest.mark.anyio
    async def test_login(
            self,
            provide_user_controller: UserController,
            provide_auth_controller: OauthController,
    ):
        user = UserFactory(id=None)
        await provide_user_controller.create(user)
        response = await provide_auth_controller.login(user.username, user.password)
        assert response.access_token
        assert response.refresh_token
        assert response.username == user.username
        assert response.email == user.email

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
        registered_user = await provide_auth_controller.register(user_data)
        assert registered_user.username == user_to_register.username
        assert registered_user.email == user_to_register.email
        assert registered_user.access_token
        assert registered_user.refresh_token
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
        response_login = await provide_auth_controller.login(user.username, user.password)
        response = await provide_auth_controller.refresh_access_token(response_login.refresh_token)
        assert response.access_token
        assert response.refresh_token
        assert response.username == user.username
        assert response.email == user.email
