from db import Database
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from schemas.users import OutputUserSchema
from services.permissions import check_operation_permission
from services.permissions.base import OperationPermission
from services.repositories.users import UserRepository

from web.dependencies import inject_database
from web.dependencies.oauth import add_auth_user_to_request

me_url_name = "users_me"
user_all_url_name = "users_all"

router = APIRouter(dependencies=[
    Depends(add_auth_user_to_request),
])


@router.get("/me", name=me_url_name)
async def get_me(
        request: Request,
        db: Database = Depends(inject_database),
        repository: UserRepository = Depends(UserRepository),
) -> OutputUserSchema:
    async with db.get_async_session() as session:
        user = await repository.get(session, request.state.user.id)
    return OutputUserSchema.model_validate(user, from_attributes=True)


@router.get("/all", name=user_all_url_name)
async def get_all(
        request: Request,
        db: Database = Depends(inject_database),
        repository: UserRepository = Depends(UserRepository),

) -> list[OutputUserSchema]:
    check_operation_permission(OperationPermission.User.can_view_list, request.state.user)
    async with db.get_async_session() as session:
        users = await repository.list(session)
    return [
        OutputUserSchema.model_validate(user, from_attributes=True)
        for user in users
    ]
