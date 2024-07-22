from __future__ import annotations

import typing
from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import IDMixin, PgBaseModel

if typing.TYPE_CHECKING:
    from .users import UserTable


class PostTable(PgBaseModel, IDMixin):
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
    author: Mapped[UserTable] = relationship(back_populates="user_posts")
    post_comments: Mapped[set[CommentTable]] = relationship(back_populates="post")


class CommentTable(PgBaseModel, IDMixin):
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
    post: Mapped[PostTable] = relationship(back_populates="post_comments")
    author_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey("users.id"), nullable=False)
    author: Mapped[UserTable] = relationship(back_populates="user_comments")