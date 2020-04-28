"""
Integration with Marshmallow library.
"""
from functools import wraps

from flask import request
from marshmallow import Schema as MMSchema

from core.utils.case import snake_to_camel_case, snake_to_hyphen_case


class CamelCaseMixin:
    """
    Applied to marshmallow Schema, forces it to use camelCase for its external
    representation and snake_case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = snake_to_camel_case(field_obj.data_key or field_name)


class HyphenCaseMixin:
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = snake_to_hyphen_case(field_obj.data_key or field_name)


class Schema(CamelCaseMixin, MMSchema):
    pass


class RequestArgsSchema(HyphenCaseMixin, MMSchema):
    pass


def expects_json(schema_class):
    schema = schema_class()

    def inner(view):
        @wraps(view)
        def wrapper(**kwargs):
            data = schema.load(request.json)
            return view(data, **kwargs)

        return wrapper

    return inner
