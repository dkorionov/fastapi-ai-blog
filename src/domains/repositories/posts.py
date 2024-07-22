from db.models import PostTable

from .base import PgCreateUpdateDeleteRepository, PgGetListRepository


class PostReadRepository(PgGetListRepository):
    model = PostTable


class PostWriteRepository(PgCreateUpdateDeleteRepository):
    model = PostTable
