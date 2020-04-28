from uuid import UUID

import jwt
from flask import g
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import Unauthorized

auth = HTTPTokenAuth()


@auth.verify_token
def verify_token(token):
    payload = validate_token(token)
    if not payload:
        return False
    g.current_user_id = payload["user_id"]
    g.permissions = payload["permissions"]
    return True


@auth.error_handler
def unauthorized():
    raise Unauthorized(www_authenticate=auth.authenticate_header())


def validate_token(token):
    try:
        public_key = ''  # get from config
        payload = jwt.decode(token, public_key, algorithms="RS256")
    except jwt.PyJWTError:
        return None
    return {
        "user_id": UUID(payload["userId"]),
        "permissions": _extract_perms(payload["permissions"]),
    }


def create_token(user_id, permissions):
    private_key = ''  # get from config
    payload = {"userId": str(user_id), "permissions": _build_perms(permissions)}
    token = jwt.encode(payload, private_key, algorithm="RS256")
    token = token.decode("utf-8")
    return token


def _extract_perms(perms):
    return [p.replace("service:", "") for p in perms if p.startswith("service:")]


def _build_perms(perms):
    return ["service:" + p for p in perms]
