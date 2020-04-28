import pytest

from werkzeug.exceptions import Unauthorized
from flask import g

from core.utils import compose
from service.auth import decorators


def test_compose__right_order(mocker):
    order = []
    f = mocker.MagicMock()
    f.return_value = 42

    def wrapper1(func):
        def inner(*args, **kwargs):
            order.append("A")
            result = func(*args, **kwargs)
            order.append("B")
            return result

        return inner

    def wrapper2(func):
        def inner(*args, **kwargs):
            order.append("C")
            result = func(*args, **kwargs)
            order.append("D")
            return result

        return inner

    def func(*args, **kwargs):
        """some doc"""
        order.append("E")
        result = f(*args, **kwargs)
        return result

    final_func = compose(wrapper1, wrapper2)(func)

    res = final_func(13, key=24)

    assert final_func.__doc__ == "some doc"
    assert res == 42
    f.assert_called_once_with(13, key=24)
    assert order == ["A", "C", "E", "D", "B"]


def test_empty_compose__ok(mocker):
    f = mocker.MagicMock()
    f.return_value = 42

    def func(*args, **kwargs):
        """some doc"""
        result = f(*args, **kwargs)
        return result

    final_func = compose()(func)

    res = final_func(13, key=24)

    assert final_func.__doc__ == "some doc"
    assert res == 42
    f.assert_called_once_with(13, key=24)


def test_has_single_permission__ok(request_context, mocker):
    g.permissions = ["annotator"]
    inner = mocker.MagicMock()
    wrapped = decorators.has_permissions("annotator")(inner)

    wrapped()

    inner.assert_called()


def test_has_no_permission__raise(request_context, mocker):
    expected = 'Bearer realm="Need permissions: tas:annotator"'
    g.permissions = []
    inner = mocker.MagicMock()
    wrapped = decorators.has_permissions("annotator")(inner)

    with pytest.raises(Unauthorized) as exc_info:
        wrapped()

    actual = exc_info.value.www_authenticate[0]
    assert actual == expected
    inner.assert_not_called()


def test_has_both_permissions__ok(request_context, mocker):
    g.permissions = ["annotator", "admin"]
    inner = mocker.MagicMock()
    wrapped = decorators.has_permissions("annotator", "admin")(inner)

    wrapped()

    inner.assert_called()


def test_lack_one_permission__raise(request_context, mocker):
    expected = 'Bearer realm="Need permissions: tas:admin, tas:another"'
    g.permissions = ["annotator"]
    inner = mocker.MagicMock()
    wrapped = decorators.has_permissions("annotator", "admin", "another")(inner)

    with pytest.raises(Unauthorized) as exc_info:
        wrapped()

    actual = exc_info.value.www_authenticate[0]
    assert actual == expected
    inner.assert_not_called()
