import random

import pytest
from db import Database
from db.models import PostModel, UserModel
from factories import PostFactory, UserFactory
from fastapi import FastAPI
from httpx import AsyncClient
from services.oauth import JwtAuthService
from sqlalchemy import select
from starlette import status
from web.api.posts import (
    create_post_url_name,
    delete_post_url_name,
    get_post_url_name,
    list_posts_url_name,
    update_post_url_name,
)

from api_tests.conftest import login_client, logout_client


@pytest.fixture(scope="function")
async def create_test_data(database_connect: Database, async_client: AsyncClient, get_jwt_service: JwtAuthService):
    async with database_connect.get_async_session() as session:
        user_1 = UserFactory()
        user_2 = UserFactory()
        session.add(user_1)
        session.add(user_2)
        await session.commit()
        posts = [PostFactory(author_id=random.choice([user_1.id, user_2.id])) for _ in range(5)]
        posts.extend([PostFactory(author_id=user_1.id), PostFactory(author_id=user_2.id)])
        session.add_all(posts)
        await session.commit()
        await session.refresh(user_1)
        login_client(async_client, user_1.id, get_jwt_service)


@pytest.mark.anyio
@pytest.mark.usefixtures("create_test_data")
class TestPostsAPI:

    async def test_unauthorized_posts(self, async_client: AsyncClient, fastapi_app: FastAPI):
        logout_client(async_client)
        response = await async_client.get(fastapi_app.url_path_for(list_posts_url_name))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_posts(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
    ):
        response = await async_client.get(fastapi_app.url_path_for(list_posts_url_name))
        assert response.status_code == status.HTTP_200_OK

    async def test_post_by_title(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
            post = PostFactory(author_id=user.id, title="Test Title")
            session.add(post)
            await session.commit()
            await session.refresh(post)
        url = fastapi_app.url_path_for(list_posts_url_name)
        response = await async_client.get(url, params={"title": post.title})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["title"] == post.title

    async def test_get_post_by_author(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
            stm = select(PostModel).where(PostModel.author_id == user.id)
            posts_by_author = await session.execute(stm)
            posts_by_author = posts_by_author.scalars().all()
        url = fastapi_app.url_path_for(list_posts_url_name)
        response = await async_client.get(url, params={"author_id": user.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(posts_by_author)

    async def test_get_post_ordering(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,

    ):
        url = fastapi_app.url_path_for(list_posts_url_name)
        response = await async_client.get(url, params={"order_by": "-id"})
        assert response.status_code == status.HTTP_200_OK

    async def test_create_post(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,

    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
        url = fastapi_app.url_path_for(create_post_url_name)
        data = {
            "title": "Test Title",
            "content": "Test Content"
        }
        response = await async_client.post(url, json=data)
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["title"] == data["title"]
        assert response_data["content"] == data["content"]
        assert response_data["author_id"] == user.id

    async def test_get_post(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
    ):
        async with database_connect.get_async_session() as session:
            post = await session.get(PostModel, 1)
        url = fastapi_app.url_path_for(get_post_url_name, post_id=post.id)
        response = await async_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == post.id

    async def test_update_post_permission_denied(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database
    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
            post = select(PostModel).where(PostModel.author_id != user.id).limit(1)
            result = await session.execute(post)
            post = result.scalars().first()
        url = fastapi_app.url_path_for(update_post_url_name, post_id=post.id)
        response = await async_client.put(url, json={"title": "New Title"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_post(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database
    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
            post = select(PostModel).where(PostModel.author_id == user.id).limit(1)
            result = await session.execute(post)
            post = result.scalars().first()
        url = fastapi_app.url_path_for(update_post_url_name, post_id=post.id)
        response = await async_client.put(url, json={"title": "New Title"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == "New Title"

    async def test_delete_post_permission_denied(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database
    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
            post = select(PostModel).where(PostModel.author_id != user.id).limit(1)
            result = await session.execute(post)
            post = result.scalars().first()
        url = fastapi_app.url_path_for(delete_post_url_name, post_id=post.id)
        response = await async_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_post(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database
    ):
        async with database_connect.get_async_session() as session:
            user = await session.get(UserModel, 1)
            post = select(PostModel).where(PostModel.author_id == user.id).limit(1)
            result = await session.execute(post)
            post = result.scalars().first()
        url = fastapi_app.url_path_for(delete_post_url_name, post_id=post.id)
        response = await async_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        async with database_connect.get_async_session() as session:
            post = await session.get(PostModel, post.id)
            assert post is None
