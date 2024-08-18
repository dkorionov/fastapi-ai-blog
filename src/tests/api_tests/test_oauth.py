import pytest
from factories.users import UserFactory
from fastapi import FastAPI, status
from httpx import AsyncClient
from schemas.oauth import RegisterSchema
from web.api.oauth import login_url_name, refresh_token_url_name, register_url_name


@pytest.mark.anyio
class TestAuthAPI:
    user_password = "test"
    test_user = UserFactory(password=user_password)

    async def test_register(self, async_client: AsyncClient, fastapi_app: FastAPI):
        url = fastapi_app.url_path_for(register_url_name)
        data = RegisterSchema(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.user_password,
        ).model_dump()
        response = await async_client.post(url, json=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["username"] == data["username"]
        assert response.json()["email"] == data["email"]

    async def test_login(self, async_client: AsyncClient, fastapi_app: FastAPI):
        await self.test_register(async_client, fastapi_app)
        url = fastapi_app.url_path_for(login_url_name)
        data = {
            "username": self.test_user.username,
            "password": self.user_password,
        }
        response = await async_client.post(url, json=data)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["username"] == data["username"]
        assert response_data["access_token"]
        assert response_data["refresh_token"]

    async def test_refresh_token(self, async_client: AsyncClient, fastapi_app: FastAPI):
        await self.test_register(async_client, fastapi_app)
        url_login = fastapi_app.url_path_for(login_url_name)
        data_login = {
            "username": self.test_user.username,
            "password": self.user_password,
        }
        response_login = await async_client.post(url_login, json=data_login)
        response_data_login = response_login.json()
        url_refresh_token = fastapi_app.url_path_for(refresh_token_url_name)
        response = await async_client.post(
            url_refresh_token,
            json={"refresh_token": response_data_login["refresh_token"]},
        )
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["username"] == data_login["username"]
        assert response_data["access_token"]
        assert response_data["refresh_token"]
