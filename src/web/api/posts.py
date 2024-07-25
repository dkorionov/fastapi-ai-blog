from domains.controllers import PostController
from domains.dto.post import PostDTO, PostFilter
from fastapi import APIRouter, Depends, Request
from services.dependencies.controllers import get_posts_controller
from services.dependencies.filters import Pagination, get_pagination, get_post_filters
from services.dependencies.oauth import (
    add_auth_user_id_to_request,
    get_current_active_user,
)
from services.schemas.posts import InputPostSchema, PostWithAuthorSchema
from services.schemas.user import OutputUserSchema

router = APIRouter(
    dependencies=[Depends(add_auth_user_id_to_request)],
)


@router.get("")
async def get_posts(
        post_controller: PostController = Depends(get_posts_controller, use_cache=True),
        pagination: Pagination = Depends(get_pagination, use_cache=True),
        filters: PostFilter = Depends(get_post_filters, use_cache=True)
) -> list[PostWithAuthorSchema]:
    result = await post_controller.get_list_with_author()
    return [PostWithAuthorSchema.model_validate(post, from_attributes=True) for post in result]


@router.post("")
async def create_post(
        request: Request,
        data: InputPostSchema,
        post_controller: PostController = Depends(get_posts_controller, use_cache=True),
        active_user: OutputUserSchema = Depends(get_current_active_user)
) -> PostWithAuthorSchema:
    post_to_create = PostDTO(
        **data.model_dump(),
        author_id=request.state.user_id,
    )
    post = await post_controller.create(post_to_create)
    return PostWithAuthorSchema(**post.model_dump(), author=active_user)


@router.get("/{post_id}")
async def get_post(
        post_id: int,
        post_controller: PostController = Depends(get_posts_controller, use_cache=True)
) -> PostWithAuthorSchema:
    post = await post_controller.get(post_id)
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)


@router.put("/{post_id}")
async def update_post(
        post_id: int,
        data: InputPostSchema,
        post_controller: PostController = Depends(get_posts_controller, use_cache=True)
) -> PostWithAuthorSchema:
    item_to_update = PostDTO(**data.model_dump(exclude=set("author_id")), id=post_id)
    post = await post_controller.update(item_to_update)
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)
