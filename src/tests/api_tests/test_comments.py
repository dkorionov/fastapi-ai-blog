import pytest
from db import Database
from factories import CommentFactory, PostFactory, UserFactory
from fastapi import FastAPI, status
from httpx import AsyncClient
from services.oauth import JwtAuthService
from web.api.comments import (
    comment_create_url_name,
    comment_list_url_name,
    comment_update_url_name,
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
        post = PostFactory(author_id=user_1.id)
        session.add(post)
        await session.commit()
        comments = [
            CommentFactory(author_id=user_1.id, post_id=post.id),
            CommentFactory(author_id=user_2.id, post_id=post.id)
        ]
        session.add_all(comments)
        await session.commit()
        await session.refresh(user_1)
        login_client(async_client, user_1.id, get_jwt_service)


@pytest.mark.anyio
@pytest.mark.usefixtures("create_test_data")
class TestCommentAPI:
    async def test_unauthorized_comments(self, async_client: AsyncClient, fastapi_app: FastAPI):
        logout_client(async_client)
        response = await async_client.get(fastapi_app.url_path_for(comment_list_url_name, post_id=1))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_comments(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
    ):
        response = await async_client.get(fastapi_app.url_path_for(comment_list_url_name, post_id=1))
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 2

    async def test_get_comments_for_non_existing_post(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
    ):
        response = await async_client.get(fastapi_app.url_path_for(comment_list_url_name, post_id=999))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_comment_permission_denied(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
            get_jwt_service: JwtAuthService,
    ):
        login_client(async_client, 2, get_jwt_service)
        response = await async_client.put(
            fastapi_app.url_path_for(comment_update_url_name, comment_id=1),
            json={"content": "Updated Content"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_comment(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            get_jwt_service: JwtAuthService,
    ):
        login_client(async_client, 2, get_jwt_service)
        response = await async_client.put(
            fastapi_app.url_path_for(comment_update_url_name, comment_id=2),
            json={"content": "Updated Content"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["content"] == "Updated Content"

    async def test_create_comment(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
    ):
        response = await async_client.post(
            fastapi_app.url_path_for(comment_create_url_name, post_id=1),
            json={"content": "New Comment"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["content"] == "New Comment"
        assert response_data["author_id"] == 1
        assert response_data["post_id"] == 1

    async def test_can_delete_post_author(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
    ):
        response = await async_client.delete(fastapi_app.url_path_for(comment_update_url_name, comment_id=2))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_can_delete_comment_author(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
            get_jwt_service: JwtAuthService,
    ):
        login_client(async_client, 2, get_jwt_service)
        response = await async_client.delete(fastapi_app.url_path_for(comment_update_url_name, comment_id=2))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_comment_permission_denied(
            self,
            async_client: AsyncClient,
            fastapi_app: FastAPI,
            database_connect: Database,
            get_jwt_service: JwtAuthService,
    ):
        # nor the author of the post or the comment
        login_client(async_client, 2, get_jwt_service)
        response = await async_client.delete(fastapi_app.url_path_for(comment_update_url_name, comment_id=1))
        assert response.status_code == status.HTTP_403_FORBIDDEN
