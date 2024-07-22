import pytest
from core.config import MainSettings
from domains.controllers import OauthController, UserController
from httpx import AsyncClient
from services.dependencies.oauth import get_oauth_controller
from services.dependencies.users import get_user_controller
from services.security import JwtAuthService


@pytest.fixture(scope="module")
def get_jwt_service(get_test_settings: MainSettings) -> JwtAuthService:
    return JwtAuthService(get_test_settings.security)


def login_client(client: AsyncClient, user_id: int, get_jwt_service: JwtAuthService):
    tokens = get_jwt_service.generate_jwt_tokens(user_id)
    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})


def logout_client(client: AsyncClient):
    client.headers.pop("Authorization")


@pytest.fixture(scope="function")
def provide_user_controller(get_test_settings: MainSettings) -> UserController:
    return get_user_controller(settings=get_test_settings)


@pytest.fixture(scope="function")
def provide_auth_controller(get_test_settings: MainSettings) -> OauthController:
    return get_oauth_controller(settings=get_test_settings)
