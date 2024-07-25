from core.config import MainSettings, create_settings
from domains.controllers import OauthController, PostController, UserController
from domains.providers import (
    provide_oauth_controller,
    provide_post_controller,
    provide_user_controller,
)
from fastapi import Depends

from .base import inject_database, inject_jwt_service


def get_user_controller(settings: MainSettings = Depends(create_settings)) -> UserController:
    return provide_user_controller(
        db=inject_database(settings=settings),
        jwt_service=inject_jwt_service(settings=settings)
    )


def get_oauth_controller(
        settings: MainSettings = Depends(create_settings)
) -> OauthController:
    return provide_oauth_controller(
        db=inject_database(settings=settings),
        jwt_service=inject_jwt_service(settings=settings)
    )


def get_posts_controller(
        settings: MainSettings = Depends(create_settings)
) -> PostController:
    return provide_post_controller(
        db=inject_database(settings=settings),
    )
