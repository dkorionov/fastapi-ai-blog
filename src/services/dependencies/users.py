from core.config import MainSettings, create_settings
from domains.controllers import UserController
from domains.providers.users import provide_user_controller
from fastapi import Depends, Request

from services.dependencies.base import inject_database, inject_jwt_service
from services.schemas.user import BaseUser


def get_user_controller(settings: MainSettings = Depends(create_settings)) -> UserController:
    return provide_user_controller(
        db=inject_database(settings=settings),
        jwt_service=inject_jwt_service(settings=settings)
    )


async def get_current_active_user(
        request: Request,
        user_controller: UserController = Depends(get_user_controller)
) -> BaseUser:
    return await user_controller.get(request.state.user_id)
