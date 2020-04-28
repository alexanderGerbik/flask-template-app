from flask import jsonify
from werkzeug import exceptions

from .mallow import snake_to_camel_case


def handle_bad_input(error):
    messages = error.normalized_messages()
    messages = {snake_to_camel_case(k): v for k, v in messages.items()}
    return jsonify(description="Invalid input.", messages=messages), 400


def jsonify_default_exceptions(app):
    """
    Converts all error responses into JSON responses.
    Returned dictionary will have single "error" key
    which holds textual representation of the error response.
    """

    def _handle_exception(error):
        headers = error.get_headers()
        headers = [h for h in headers if h[0] != "Content-Type"]
        return jsonify(error=error.description), error.code, headers

    for ex in exceptions.default_exceptions:
        app.register_error_handler(ex, _handle_exception)
