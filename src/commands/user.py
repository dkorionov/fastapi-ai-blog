import asyncio

import click
from core.config import MainSettings, create_settings
from core.config.constansts import UserRole
from db import Database
from db.models import UserModel
from services.oauth import JwtAuthService


async def create_admin_command(
        username: str,
        email: str,
        password: str,
        settings: MainSettings
):
    db = Database(settings.db)
    jwt_service = JwtAuthService(security_settings=settings.security)
    password = jwt_service.hash_password(password)
    async with db.get_async_session() as session:
        new_admin = UserModel(
            username=username,
            email=email,
            password=password,
            role=UserRole.ADMIN
        )
        session.add(new_admin)
        await session.commit()

    click.echo(f"User {new_admin.username} has been created")


@click.command()
@click.argument("username", type=str)
@click.argument("email", type=str)
@click.argument("password", type=str)
def create_admin(username: str, email: str, password: str):
    asyncio.run(create_admin_command(
        username=username,
        email=email,
        password=password,
        settings=create_settings()
    ))
