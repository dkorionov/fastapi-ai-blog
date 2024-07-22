from domains.controllers.base import BaseController
from domains.repositories.posts import PostReadRepository, PostWriteRepository


class PostsController(BaseController):
    def __init__(
            self,
            read_repo: PostReadRepository,
            write_repo: PostWriteRepository,
    ):
        self.read_repo = read_repo
        self.write_repo = write_repo

    async def get_posts(self):
        async with self.read_repo.session_factory() as session:
            return await self.read_repo.get_list(session)

    async def create_post(self, data):
        async with self.write_repo.session_factory() as session:
            return await self.write_repo.create(session, data)
