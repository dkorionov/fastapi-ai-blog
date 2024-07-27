from domains.controllers import PostController
from domains.dto import UserDTO
from domains.dto.post import PostDTO, PostFilter
from domains.permissions import OperationPermission
from fastapi import APIRouter, Depends, Request
from services.dependencies.controllers import get_post_controller
from services.dependencies.filters import Pagination, get_pagination, get_post_filters
from services.dependencies.oauth import (
    add_auth_user_id_to_request,
    check_operation_permission,
    check_route_permission,
    get_current_active_user,
)
from services.schemas.posts import InputPostSchema, PostWithAuthorSchema
from services.schemas.user import OutputUserSchema
from services.security.oauth import check_object_permission

router = APIRouter(
    dependencies=[Depends(add_auth_user_id_to_request)],
)


@check_route_permission(OperationPermission.Post.can_view_list)
@router.get("")
async def get_posts(
        post_controller: PostController = Depends(get_post_controller, use_cache=True),
        pagination: Pagination = Depends(get_pagination, use_cache=True),
        filters: PostFilter = Depends(get_post_filters, use_cache=True)
) -> list[PostWithAuthorSchema]:
    result = await post_controller.get_list_with_author(
        filters,
        offset=pagination.offset,
        limit=pagination.limit
    )
    return [PostWithAuthorSchema.model_validate(post, from_attributes=True) for post in result]


@router.post("")
async def create_post(
        request: Request,
        data: InputPostSchema,
        post_controller: PostController = Depends(get_post_controller, use_cache=True),
        active_user: UserDTO = Depends(get_current_active_user)
) -> PostWithAuthorSchema:
    check_operation_permission(OperationPermission.Post.can_create, active_user)
    post_to_create = PostDTO(
        **data.model_dump(),
        author_id=request.state.user_id,
    )
    post = await post_controller.create(post_to_create)
    return PostWithAuthorSchema(
        **post.model_dump(),
        author=OutputUserSchema.model_validate(
            active_user, from_attributes=True
        )
    )


@router.get("/{post_id}")
async def get_post(
        post_id: int,
        post_controller: PostController = Depends(get_post_controller, use_cache=True),
        active_user: UserDTO = Depends(get_current_active_user)
) -> PostWithAuthorSchema:
    post = await post_controller.get(post_id)
    check_object_permission(OperationPermission.Post.can_view, active_user, post)
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)


@router.put("/{post_id}")
async def update_post(
        post_id: int,
        data: InputPostSchema,
        post_controller: PostController = Depends(get_post_controller, use_cache=True),
        active_user: UserDTO = Depends(get_current_active_user)
) -> PostWithAuthorSchema:
    item_to_update = await post_controller.get(post_id)
    check_object_permission(OperationPermission.Post.can_update, active_user, item_to_update)
    post = await post_controller.update(PostDTO(**data.model_dump(exclude_unset=True), id=post_id))
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)
