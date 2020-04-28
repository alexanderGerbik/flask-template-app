import jwt
import pytest
from flask import g
from werkzeug.exceptions import Unauthorized

from service.auth import token as token_module


def test_user_unauthorized__raise():
    expected = 'Bearer realm="Authentication Required"'

    with pytest.raises(Unauthorized) as exc_info:
        token_module.unauthorized()

    actual = exc_info.value.www_authenticate[0]
    assert actual == expected


def test_verify_token_valid__set_permissions_user_id(request_context, mocker):
    token = "some_token"
    validate_token = mocker.patch.object(token_module, "validate_token")
    validate_token.return_value = dict(user_id=13, permissions=["A", "B"])

    is_valid = token_module.verify_token(token)

    assert is_valid
    assert g.current_user_id == 13
    assert g.permissions == ["A", "B"]


def test_verify_token_invalid__default_permissions_user_id(request_context, mocker):
    token = "some_token"
    validate_token = mocker.patch.object(token_module, "validate_token")
    validate_token.return_value = None

    is_valid = token_module.verify_token(token)

    assert not is_valid
    assert g.current_user_id is None
    assert g.permissions == []


def test_verify_token_delegates_to_validate_token(request_context, mocker):
    token = "some_token"
    validate_token = mocker.patch.object(token_module, "validate_token")
    validate_token.return_value = dict(user_id=13, permissions=["A", "B"])

    token_module.verify_token(token)

    validate_token.assert_called_once_with(token)


def test_token_is_forged__validate_fails(app):
    actual_user = token_module.validate_token("some_random_value")

    assert actual_user is None
