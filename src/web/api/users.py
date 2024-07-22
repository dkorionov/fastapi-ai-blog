from core.config.constansts import UserRole
from domains.controllers import UserController
from fastapi import APIRouter, Depends, Request
from services.dependencies.oauth import add_auth_user_id_to_request, has_permission
from services.dependencies.users import get_user_controller
from services.schemas.user import BaseUser

me_url_name = "users_me"
user_all_url_name = "users_all"

router = APIRouter(dependencies=[
    Depends(add_auth_user_id_to_request),
])


@router.get("/me", name=me_url_name)
async def get_me(
        request: Request,
        user_controller: UserController = Depends(get_user_controller)
) -> BaseUser:
    return await user_controller.get(request.state.user_id)


@router.get("/all", dependencies=[Depends(has_permission([UserRole.ADMIN]))], name=user_all_url_name)
async def get_all(
        user_controller: UserController = Depends(get_user_controller),
) -> list[BaseUser]:
    return await user_controller.list()
