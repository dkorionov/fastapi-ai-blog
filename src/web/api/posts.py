from db import Database
from db.models import PostModel
from fastapi import APIRouter, Depends, Request, Response
from schemas.posts import InputPostSchema, PostWithAuthorSchema, UpdatePostSchema
from services.permissions import check_object_permission, check_operation_permission
from services.permissions.base import OperationPermission
from services.repositories.posts import PostRepository

from web.dependencies import inject_database
from web.dependencies.filters import get_ordering, get_pagination, get_post_filters
from web.dependencies.oauth import (
    add_auth_user_to_request,
)

list_posts_url_name = "posts_list"
create_post_url_name = "posts_create"
get_post_url_name = "posts_get"
update_post_url_name = "posts_update"
delete_post_url_name = "posts_delete"

router = APIRouter(
    dependencies=[Depends(add_auth_user_to_request)],
)


@router.get("", name=list_posts_url_name)
async def get_post_list(
        request: Request,
        db: Database = Depends(inject_database),
        pagination=Depends(get_pagination),
        filters=Depends(get_post_filters),
        ordering=Depends(get_ordering),
        repository=Depends(PostRepository),
) -> list[PostWithAuthorSchema]:
    check_operation_permission(OperationPermission.Post.can_view_list, request.state.user)
    async with db.get_async_session() as session:
        posts = await repository.get_posts_with_author(session, filters, ordering, pagination)
    return [PostWithAuthorSchema.model_validate(post, from_attributes=True) for post in posts]


@router.post("", name=create_post_url_name, status_code=201)
async def create_post(
        request: Request,
        data: InputPostSchema,
        db: Database = Depends(inject_database),
        repository=Depends(PostRepository),
) -> PostWithAuthorSchema:
    check_operation_permission(OperationPermission.Post.can_create, request.state.user)
    post = PostModel(
        **data.model_dump(),
        author_id=request.state.user.id,
    )
    async with db.get_async_session() as session:
        await repository.create(session, post)
        post = await repository.get_with_author(session, post.id)
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)


@router.get("/{post_id}", name=get_post_url_name)
async def get_post(
        request: Request,
        post_id: int,
        db: Database = Depends(inject_database),
        repository=Depends(PostRepository)

) -> PostWithAuthorSchema:
    async with db.get_async_session() as session:
        post = await repository.get_with_author(session, post_id)
    check_object_permission(OperationPermission.Post.can_view, request.state.user, post)
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)


@router.put("/{post_id}", name=update_post_url_name)
async def update_post(
        request: Request,
        post_id: int,
        data: UpdatePostSchema,
        db: Database = Depends(inject_database),
        repository=Depends(PostRepository)
) -> PostWithAuthorSchema:
    async with db.get_async_session() as session:
        post = await repository.get(session, post_id)
        check_object_permission(OperationPermission.Post.can_update, request.state.user, post)
        await repository.update(session, post.id, data.model_dump(
            exclude_unset=True, exclude_defaults=True
        ))
        post = await repository.get_with_author(session, post_id)
    return PostWithAuthorSchema.model_validate(post, from_attributes=True)


@router.delete("/{post_id}", status_code=204, name=delete_post_url_name)
async def delete_post(
        request: Request,
        post_id: int,
        db: Database = Depends(inject_database),
        repository=Depends(PostRepository)
):
    async with db.get_async_session() as session:
        post = await repository.get(session, post_id)
        check_object_permission(OperationPermission.Post.can_delete, request.state.user, post)
        await repository.delete(session, post_id)
    return Response(status_code=204)
