from __future__ import annotations

from datetime import datetime

import sqlalchemy
from core.config.constansts import UserRole
from sqlalchemy.orm import Mapped, mapped_column

from .base import IDMixin, PgBaseModel


class UserTable(PgBaseModel, IDMixin):
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
