import pytest
from core.config.constansts import UserRole
from domains.controllers import UserController
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status
from web.api.users import me_url_name, user_all_url_name

from tests.api_tests.conftest import login_client
from tests.factories.user import UserFactory


class TestUserAPI:

    @pytest.mark.anyio
    async def test_me_unauthorized(self, async_client: AsyncClient, fastapi_app: FastAPI):
        url = fastapi_app.url_path_for(me_url_name)
        response = await async_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_me(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            provide_user_controller: UserController
    ):
        url = fastapi_app.url_path_for(me_url_name)
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        login_client(async_client, created_user.id, provide_user_controller.oauth_service)
        response = await async_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["username"] == user_to_create.username
        assert response_data["email"] == user_to_create.email
        assert response_data["id"] == created_user.id

    @pytest.mark.anyio
    async def test_all_permission_denied(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            provide_user_controller: UserController
    ):
        url = fastapi_app.url_path_for(user_all_url_name)
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        login_client(async_client, created_user.id, provide_user_controller.oauth_service)
        response = await async_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.anyio
    async def test_get_all(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            provide_user_controller: UserController
    ):
        url = fastapi_app.url_path_for(user_all_url_name)
        admin_to_create = UserFactory(id=None, role=UserRole.ADMIN)
        await provide_user_controller.create_user_bulk([UserFactory(id=None) for _ in range(5)])
        created_admin = await provide_user_controller.create(admin_to_create)
        login_client(async_client, created_admin.id, provide_user_controller.oauth_service)
        response = await async_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(response_data) == 6
