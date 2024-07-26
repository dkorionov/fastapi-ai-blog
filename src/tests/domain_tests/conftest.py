from domains.controllers import UserController
from domains.dto import UserDTO
from factories import UserFactory
from pytest import fixture


@fixture
async def provide_author(provide_user_controller: UserController) -> UserDTO:
    return await provide_user_controller.create(UserFactory(id=None))
