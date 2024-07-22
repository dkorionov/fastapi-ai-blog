import pytest
from domains.controllers import UserController
from services.errors import ResourceNotFoundError

from tests.factories.user import UserFactory


class TestUserController:
    @pytest.mark.anyio
    async def test_create_user(self, provide_user_controller: UserController):
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        assert user_to_create.username == created_user.username
        assert user_to_create.email == created_user.email
        assert provide_user_controller.oauth_service.verify_password(user_to_create.password, created_user.password)

    @pytest.mark.anyio
    async def test_get_user(self, provide_user_controller: UserController):
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        user = await provide_user_controller.get(created_user.id)
        assert user == created_user

    @pytest.mark.anyio
    async def test_list_users(self, provide_user_controller: UserController):
        users_to_create = [UserFactory(id=None) for _ in range(5)]
        created_count = await provide_user_controller.create_user_bulk(users_to_create)
        user_list = await provide_user_controller.list()
        assert created_count == len(user_list)
        for created_user, user in zip(users_to_create, user_list):
            assert created_user.username == user.username
            assert created_user.email == user.email
            assert provide_user_controller.oauth_service.verify_password(created_user.password, user.password)

    @pytest.mark.anyio
    async def test_update_user(self, provide_user_controller: UserController):
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        created_user.username = "new_username"
        created_user.email = "new@mail.com"
        updated_user = await provide_user_controller.update(created_user)
        assert updated_user.username == created_user.username
        assert updated_user.email == created_user.email

    @pytest.mark.anyio
    async def test_delete_user(self, provide_user_controller: UserController):
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        await provide_user_controller.delete(created_user.id)
        with pytest.raises(ResourceNotFoundError):
            await provide_user_controller.get(created_user.id)

    @pytest.mark.anyio
    async def test_create_bulk_users(self, provide_user_controller: UserController):
        users_to_create = [UserFactory(id=None) for _ in range(5)]
        created_count = await provide_user_controller.create_user_bulk(users_to_create)
        assert created_count == 5

    @pytest.mark.anyio
    async def test_set_password(self, provide_user_controller: UserController):
        user_to_create = UserFactory(id=None)
        created_user = await provide_user_controller.create(user_to_create)
        new_password = "new_password"
        await provide_user_controller.set_password(created_user.id, new_password)
        updated_user = await provide_user_controller.get(created_user.id)
        assert provide_user_controller.oauth_service.verify_password(new_password, updated_user.password)
