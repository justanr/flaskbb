from flask import _request_ctx_stack, has_request_context, request
from flask_login import current_user
from werkzeug.local import LocalProxy

from ..forum.locals import current_category, current_forum
from .models import Permission
from .utils import PermissionManager


@LocalProxy
def current_permissions():
    if (
        has_request_context()
        and not getattr(_request_ctx_stack.top, "permissions", None)
    ):
        permissions = PermissionManager(
            all_perms=Permission.query.all(),
            user=current_user,
            forum=current_forum,
            category=current_category,
        )
        _request_ctx_stack.top.permissions = permissions
    return getattr(_request_ctx_stack.top, "permissions", None)
