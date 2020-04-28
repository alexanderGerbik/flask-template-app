from functools import wraps

from flask import g
from werkzeug.exceptions import Unauthorized

from .token import _build_perms, auth as _auth


def has_permissions(*permissions):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            violations = [p for p in permissions if p not in g.permissions]
            if violations:
                violations = ", ".join(_build_perms(violations))
                message = f'Bearer realm="Need permissions: {violations}"'
                raise Unauthorized(www_authenticate=message)
            return func(*args, **kwargs)

        return wrapper

    return inner


login_required = _auth.login_required
