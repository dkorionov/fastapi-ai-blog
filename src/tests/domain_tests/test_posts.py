import pytest
from domains.controllers import PostController
from domains.dto import UserDTO
from factories import PostFactory


class TestPosts:
    @pytest.mark.anyio
    async def test_create_post(
            self,
            provide_post_controller: PostController,
            provide_author: UserDTO
    ):
        post_to_create = PostFactory(id=None, author_id=provide_author.id)
        created_post = await provide_post_controller.create(post_to_create)
        assert post_to_create.title == created_post.title
        assert post_to_create.content == created_post.content

    @pytest.mark.anyio
    async def test_get_post(
            self,
            provide_post_controller: PostController,
            provide_author: UserDTO

    ):
        post_to_create = PostFactory(id=None, author_id=provide_author.id)
        created_post = await provide_post_controller.create(post_to_create)
        post = await provide_post_controller.get(created_post.id)
        assert post == created_post

    @pytest.mark.anyio
    async def test_list_posts(
            self,
            provide_post_controller: PostController,
            provide_author: UserDTO
    ):
        posts_to_create = [PostFactory(id=None, author_id=provide_author.id) for _ in range(5)]
        created = await provide_post_controller.create_bulk(posts_to_create)
        post_list = await provide_post_controller.list()
        assert len(created) == len(post_list)
        for created_post, post in zip(posts_to_create, post_list):
            assert created_post.title == post.title
            assert created_post.content == post.content

    @pytest.mark.anyio
    async def test_update_post(
            self,
            provide_post_controller: PostController,
            provide_author: UserDTO
    ):
        post_to_create = PostFactory(id=None, author_id=provide_author.id)
        created_post = await provide_post_controller.create(post_to_create)
        created_post.title = "new_title"
        created_post.content = "new content"
        updated_post = await provide_post_controller.update(created_post)
        assert updated_post.title == created_post.title
        assert updated_post.content == created_post.content
