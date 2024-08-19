from typing import Tuple

from db.models import CommentModel

from services.permissions.base import (
    AbstractObjectPermission,
    OperationPermission,
    PermissionRoles,
)


class CommentPermissions(AbstractObjectPermission):

    @staticmethod
    def get_object_lvl_permission(model_object: CommentModel) -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Comment.can_update, [model_object.author_id]),
            (OperationPermission.Comment.can_delete, [
                PermissionRoles.admin.value,
                model_object.author_id,
                model_object.post.author_id
            ]),
        ]

    @staticmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Comment.can_create, [PermissionRoles.all.value]),
            (OperationPermission.Comment.can_view, [PermissionRoles.all.value]),
        ]
