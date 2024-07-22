from core.config import MainSettings, create_settings
from db import Database
from fastapi import Depends

from services.security import JwtAuthService


def inject_database(
        settings: MainSettings = Depends(create_settings)

) -> Database:
    """
    Create and return database instance.

    :return: database instance.
    """
    return Database(settings.db)


def inject_jwt_service(settings: MainSettings = Depends(create_settings)) -> JwtAuthService:
    """
    Create and return jwt service instance.

    :return: jwt service instance.
    """
    return JwtAuthService(security_settings=settings.security)
