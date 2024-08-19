from typing import cast

import pytest
from core.config.constansts import UserRole
from db import Database
from db.models import UserModel
from factories import UserFactory
from fastapi import FastAPI
from httpx import AsyncClient
from services.oauth import JwtAuthService
from services.repositories.users import UserRepository
from starlette import status
from tests.api_tests.conftest import login_client
from web.api.users import me_url_name, user_all_url_name


class TestUserAPI:
    repository = UserRepository()

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
            database_connect: Database,
            get_jwt_service: JwtAuthService,
    ):
        async with database_connect.get_async_session() as session:
            user = await self.repository.create(session, UserFactory(id=None))
            user = cast(UserModel, user)

        login_client(async_client, user.id, get_jwt_service)
        url = fastapi_app.url_path_for(me_url_name)
        response = await async_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["username"] == user.username
        assert response_data["email"] == user.email
        assert response_data["id"] == user.id

    @pytest.mark.anyio
    async def test_all_permission_denied(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
            get_jwt_service: JwtAuthService,
    ):
        url = fastapi_app.url_path_for(user_all_url_name)
        async with database_connect.get_async_session() as session:
            user = await self.repository.create(session, UserFactory(id=None))
            user = cast(UserModel, user)

        login_client(async_client, user.id, get_jwt_service)
        response = await async_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.anyio
    async def test_get_all(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
            get_jwt_service: JwtAuthService,
    ):
        url = fastapi_app.url_path_for(user_all_url_name)
        async with database_connect.get_async_session() as session:
            admin = await self.repository.create(session, UserFactory(id=None, role=UserRole.ADMIN))
            await self.repository.create_bulk(session, [UserFactory(id=None) for _ in range(5)])

        login_client(async_client, admin.id, get_jwt_service)
        response = await async_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(response_data) == 6
