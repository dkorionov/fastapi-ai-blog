from domains.controllers.base import BaseCrudController
from domains.dto import PostDTO
from domains.dto.post import PostFilter
from domains.repositories.post import PostReadRepository, PostWriteRepository


class PostController(BaseCrudController):
    model_dto = PostDTO

    def __init__(
            self,
            read_repo: PostReadRepository,
            write_repo: PostWriteRepository,
    ):
        self.read_repo: PostReadRepository = read_repo
        self.write_repo: PostWriteRepository = write_repo

    async def get_list_with_author(
            self,
            filters: PostFilter = None,
            offset: int = 0,
            limit: int = 10
    ) -> list[PostDTO]:
        async with self.read_repo.session_factory() as session:
            posts_in_db = await self.read_repo.list_posts_with_author(session, filters, offset, limit)
        return [self.model_dto.model_validate(post, from_attributes=True) for post in posts_in_db]
