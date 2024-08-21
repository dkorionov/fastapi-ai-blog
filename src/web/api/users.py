from db import Database
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from schemas.users import (
    OutputUserSchema,
    UpdateUserSettingsSchema,
    UserWithSettingsSchema,
)
from services.permissions import check_operation_permission
from services.permissions.base import OperationPermission
from services.repositories.users import UserRepository, UserSettingsRepository

from web.dependencies import inject_database
from web.dependencies.oauth import add_auth_user_to_request

me_url_name = "users_me"
user_all_url_name = "users_all"
user_settings_url_name = "users_settings"

router = APIRouter(dependencies=[
    Depends(add_auth_user_to_request),
])


@router.get("/me", name=me_url_name)
async def get_me(
        request: Request,
        db: Database = Depends(inject_database),
        repository: UserRepository = Depends(UserRepository),
) -> UserWithSettingsSchema:
    async with db.get_async_session() as session:
        user = await repository.get(session, request.state.user.id, joined=[repository.model.settings])
    return UserWithSettingsSchema.model_validate(user, from_attributes=True)


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


@router.patch("/me/settings", name=user_settings_url_name)
async def update_user_settings(
        request: Request,
        data: UpdateUserSettingsSchema,
        db: Database = Depends(inject_database),
        settings_repository: UserSettingsRepository = Depends(UserSettingsRepository),
) -> UserWithSettingsSchema:
    user = request.state.user
    async with db.get_async_session() as session:
        await settings_repository.update(
            session, user.settings.id, data.model_dump(exclude_defaults=True, exclude_none=True)
        )
    return UserWithSettingsSchema.model_validate(user, from_attributes=True)
