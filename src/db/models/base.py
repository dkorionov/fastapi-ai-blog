from __future__ import annotations

import sqlalchemy
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


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


class AbstractModel(PgBaseModel, IDMixin):
    __abstract__ = True

