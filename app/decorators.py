# WHAT: @role_required("reviewer") lets only certain roles call an endpoint.
# WHY:  Write the role check once, and reuse it on any route with one line.

from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.errors import error


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)  # keeps the real function name (see the example below)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()  # no token or a bad token -> 401
            if get_jwt().get("role") not in roles:
                return error("you don't have permission to do this", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator