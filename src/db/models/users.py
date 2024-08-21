from __future__ import annotations

import typing
from datetime import datetime, timedelta

import sqlalchemy
from core.config.constansts import UserRole
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AbstractModel

if typing.TYPE_CHECKING:
    from .posts import CommentModel, PostModel


class UserModel(AbstractModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(sqlalchemy.String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sqlalchemy.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sqlalchemy.String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sqlalchemy.Enum(UserRole),
        nullable=False,
        default=UserRole.USER
    )
    joined_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        server_onupdate=sqlalchemy.func.now()
    )
    user_posts: Mapped[set[PostModel]] = relationship(back_populates="author")
    user_comments: Mapped[set[CommentModel]] = relationship(back_populates="author")
    settings: Mapped[UserSettingsModel] = relationship(back_populates="user", lazy="selectin")


class UserSettingsModel(AbstractModel):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    user: Mapped[UserModel] = relationship(back_populates="settings")
    auto_comment_answer: Mapped[bool] = mapped_column(
        sqlalchemy.Boolean,
        nullable=False,
        default=False
    )
    auto_answer_delay: Mapped[datetime.time] = mapped_column(
        sqlalchemy.Time,
        nullable=False,
        default=(datetime.min + timedelta(minutes=5)).time
    )
