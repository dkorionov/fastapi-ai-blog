from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

if TYPE_CHECKING:
    from .user import UserTable


class PgBaseModel(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = ()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"{self.__class__.__name__} ({', '.join(cols)})"


class IDMixin:
    id: Mapped[int] = mapped_column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)


class UserRelationMixin:
    _user_id_nullable: bool = False
    _user_id_unique: bool = False
    _user_back_populates: str | None = None

    @classmethod
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id"),
            unique=cls._user_id_unique,
            nullable=cls._user_id_nullable,
        )

    @classmethod
    @declared_attr
    def user(cls) -> Mapped[UserTable]:
        return relationship(
            "User",
            back_populates=cls._user_back_populates,
        )
