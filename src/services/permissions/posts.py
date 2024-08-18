from typing import Tuple

from db.models import PostModel
from services.permissions.base import AbstractObjectPermission, OperationPermission, PermissionRoles


class PostPermissions(AbstractObjectPermission):

    @staticmethod
    def get_object_lvl_permission(model_object: PostModel) -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Post.can_update, [model_object.author_id]),
            (OperationPermission.Post.can_delete, [PermissionRoles.admin.value, model_object.author_id]),
            (OperationPermission.Post.can_view, [PermissionRoles.all.value]),
        ]

    @staticmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Post.can_create, [PermissionRoles.all.value]),
            (OperationPermission.Post.can_view_list, [PermissionRoles.all.value]),
        ]
