from db import Database
from services.security import JwtAuthService

from domains.controllers import OauthController, PostController, UserController
from domains.repositories.post import PostReadRepository, PostWriteRepository
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


def provide_user_controller(
        db: Database,
        jwt_service: JwtAuthService

) -> UserController:
    read_repo = UserReadDBRepository(session_factory=db.session_factory)
    write_repo = UserWriteDBRepository(session_factory=db.session_factory)
    return UserController(
        read_repo=read_repo,
        write_repo=write_repo,
        oauth_service=jwt_service
    )


def provide_post_controller(
        db: Database,
) -> PostController:
    read_repo = PostReadRepository(session_factory=db.session_factory)
    write_repo = PostWriteRepository(session_factory=db.session_factory)
    return PostController(
        read_repo=read_repo,
        write_repo=write_repo
    )
