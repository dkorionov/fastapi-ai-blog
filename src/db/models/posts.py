from __future__ import annotations

import typing
from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AbstractModel

if typing.TYPE_CHECKING:
    from .users import UserModel


class PostModel(AbstractModel):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(sqlalchemy.String(128), nullable=False)
    content: Mapped[str] = mapped_column(sqlalchemy.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
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
    author_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey("users.id"), nullable=False)
    author: Mapped[UserModel] = relationship(back_populates="user_posts")
    post_comments: Mapped[set[CommentModel]] = relationship(back_populates="post")


class CommentModel(AbstractModel):
    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(sqlalchemy.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
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
    post_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey("posts.id"), nullable=False)
    post: Mapped[PostModel] = relationship(back_populates="post_comments")
    author_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey("users.id"), nullable=False)
    author: Mapped[UserModel] = relationship(back_populates="user_comments")
