from dataclasses import dataclass
from typing import NamedTuple

Pagination = NamedTuple("Pagination", [("limit", int), ("offset", int)])


@dataclass(frozen=True, slots=False)
class PostFilter:
    title: str | None
    author_id: int | None
