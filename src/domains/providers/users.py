from db import Database
from services.security import JwtAuthService

from domains.controllers import UserController
from domains.repositories.user import UserReadDBRepository, UserWriteDBRepository


def provide_user_controller(
        db: Database,
        jwt_service: JwtAuthService

) -> UserController:
    read_repo = UserReadDBRepository(session_factory=db.session_factory)
    write_repo = UserWriteDBRepository(session_factory=db.session_factory)
    return UserController(
        db_read_repo=read_repo,
        db_write_repo=write_repo,
        oauth_service=jwt_service
    )
