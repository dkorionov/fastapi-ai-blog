import pytest
from core.config import MainSettings
from httpx import AsyncClient
from services.security import JwtAuthService


@pytest.fixture(scope="module")
def get_jwt_service(get_test_settings: MainSettings) -> JwtAuthService:
    return JwtAuthService(get_test_settings.security)


def login_client(client: AsyncClient, user_id: int, get_jwt_service: JwtAuthService):
    tokens = get_jwt_service.generate_jwt_tokens(user_id)
    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})


def logout_client(client: AsyncClient):
    client.headers.pop("Authorization")
