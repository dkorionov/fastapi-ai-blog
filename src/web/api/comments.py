from db import Database
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from schemas.comments import (
    InputCommentSchema,
    OutputCommentSchema,
)
from services.permissions import check_object_permission, check_operation_permission
from services.permissions.base import OperationPermission
from services.repositories.comments import CommentRepository
from services.repositories.posts import PostRepository

from web.dependencies import inject_database
from web.dependencies.oauth import add_auth_user_to_request

router = APIRouter(dependencies=[Depends(add_auth_user_to_request)])

comment_create_url_name = "create_comment"
comment_update_url_name = "update_comment"
comment_delete_url_name = "delete_comment"
comment_list_url_name = "list_comments"


@router.post(
    "/{post_id}/create_comment",
    name=comment_create_url_name,
    response_model=OutputCommentSchema,
    status_code=201
)
async def create_comment(
        request: Request,
        post_id: int,
        data: InputCommentSchema,
        db: Database = Depends(inject_database),
        repository: CommentRepository = Depends(CommentRepository),
) -> OutputCommentSchema:
    check_operation_permission(OperationPermission.Comment.can_create, request.state.user)
    async with db.get_async_session() as session:
        comment_to_create = repository.model(
            **data.model_dump(),
            author_id=request.state.user.id,
            post_id=post_id
        )
        comment = await repository.create(session, comment_to_create)
    return OutputCommentSchema.model_validate(comment, from_attributes=True)


@router.put("/{comment_id}", name=comment_update_url_name, response_model=OutputCommentSchema)
async def update_comment(
        request: Request,
        comment_id: int,
        data: InputCommentSchema,
        db: Database = Depends(inject_database),
        repository: CommentRepository = Depends(CommentRepository),
) -> OutputCommentSchema:
    async with db.get_async_session() as session:
        comment = await repository.get(session, comment_id)
        check_object_permission(OperationPermission.Comment.can_update, request.state.user, comment)
        await repository.update(session, comment.id, data.model_dump(exclude_unset=True, exclude_defaults=True))
    return OutputCommentSchema.model_validate(comment, from_attributes=True)


@router.delete("/{comment_id}", name=comment_delete_url_name, status_code=204)
async def delete_comment(
        request: Request,
        comment_id: int,
        db: Database = Depends(inject_database),
        repository: CommentRepository = Depends(CommentRepository),
) -> None:
    async with db.get_async_session() as session:
        comment = await repository.get(session, comment_id)
        check_object_permission(OperationPermission.Comment.can_delete, request.state.user, comment)
        await repository.delete(session, comment.id)


@router.get("/{post_id}", name=comment_list_url_name)
async def get_comments(
        request: Request,
        post_id: int,
        db: Database = Depends(inject_database),
        post_repository: PostRepository = Depends(PostRepository),
        repository: CommentRepository = Depends(CommentRepository),
) -> list[OutputCommentSchema]:
    check_operation_permission(OperationPermission.Comment.can_view, request.state.user)
    async with db.get_async_session() as session:
        await post_repository.get(session, post_id)
        comments = await repository.get_comments_with_author(session, filters={"post_id": post_id})
    return [OutputCommentSchema.model_validate(comment, from_attributes=True) for comment in comments]
