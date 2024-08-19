from fastapi.routing import APIRouter

from .comments import router as comment_router
from .oauth import router as auth_router
from .posts import router as post_router
from .users import router as user_router

__all__ = [
    "v1_api_router",
]

v1_api_router = APIRouter(prefix="/v1")


@v1_api_router.get("/healthcheck", name="health_check")
async def healthcheck():
    return {"status": "ok"}


v1_api_router.include_router(auth_router, tags=["auth"], prefix="/oauth")
v1_api_router.include_router(user_router, tags=["users"], prefix="/users")
v1_api_router.include_router(post_router, tags=["posts"], prefix="/posts")
v1_api_router.include_router(comment_router, tags=["comments"], prefix="/comments")
