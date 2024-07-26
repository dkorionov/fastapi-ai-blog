from domains.controllers import UserController
from domains.permissions import OperationPermission
from fastapi import APIRouter, Depends, Request
from services.dependencies import get_user_controller
from services.dependencies.oauth import (
    add_auth_user_id_to_request,
    check_operation_permission,
    get_current_active_user,
)
from services.schemas.user import OutputUserSchema

me_url_name = "users_me"
user_all_url_name = "users_all"

router = APIRouter(dependencies=[
    Depends(add_auth_user_id_to_request),
])


@router.get("/me", name=me_url_name)
async def get_me(
        request: Request,
        user_controller: UserController = Depends(get_user_controller)
) -> OutputUserSchema:
    output_user = await user_controller.get(request.state.user_id)
    return OutputUserSchema.model_validate(output_user, from_attributes=True)


@router.get("/all", name=user_all_url_name)
async def get_all(
        request: Request,
        user_controller: UserController = Depends(get_user_controller),

) -> list[OutputUserSchema]:
    active_user = await get_current_active_user(request, user_controller)
    check_operation_permission(OperationPermission.User.can_view_list, active_user)
    return [
        OutputUserSchema.model_validate(user, from_attributes=True)
        for user in await user_controller.list()
    ]
