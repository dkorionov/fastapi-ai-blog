import asyncio

import click
from core.config import MainSettings, create_settings
from core.config.constansts import UserRole
from services.dependencies.users import get_user_controller


async def create_admin_command(
        username: str,
        email: str,
        password: str,
        settings: MainSettings
):
    user_controller = get_user_controller(settings=settings)
    password = user_controller.hash_password(password)
    async with user_controller.db_write_repo.session_factory() as session:
        new_admin = await user_controller.db_write_repo.create(
            session,
            {
                "username": username,
                "email": email,
                "password": password,
                "role": UserRole.ADMIN
            }
        )

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
