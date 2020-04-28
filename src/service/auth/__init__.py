from flask import Blueprint, g

from .decorators import (
    has_permissions,
    login_required,
)

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def _set_current_user():
    g.current_user_id = None
    g.permissions = []


from . import routes  # noqa: F401,E402 isort:skip
