import asyncio
from typing import cast

import click
from click.core import Command
from commands.user import create_admin


@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli.add_command(cast(Command, create_admin))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cli())
