from db import Database
from services.security import JwtAuthService

from domains.controllers import OauthController
from domains.repositories.user import UserReadDBRepository, UserWriteDBRepository


def provide_oauth_controller(
        db: Database,
        jwt_service: JwtAuthService

) -> OauthController:
    read_repo = UserReadDBRepository(session_factory=db.session_factory)
    write_repo = UserWriteDBRepository(session_factory=db.session_factory)
    return OauthController(
        read_repo=read_repo,
        write_repo=write_repo,
        jwt_service=jwt_service
    )
