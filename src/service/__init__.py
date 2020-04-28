import logging.config

from flask import Flask, g
from marshmallow.exceptions import ValidationError as MMValidationError

from core.database import configure_session, session as _session

from . import auth, cli, config, error_handlers, receivers
from .auth import test_helpers


def create_app(extra_config=None):
    app = Flask(__name__)
    app.config.from_pyfile("config/default.py")
    app.config.from_pyfile(config.choose_config())
    app.config.from_mapping(extra_config or {})
    logging.config.dictConfig(app.config["LOGGING"])

    if not app.config["TESTING"]:
        receivers.group.connect()

        configure_session(app.config)

        @app.teardown_appcontext
        def shutdown_session(response_or_exc):
            _session.remove()
            return response_or_exc

    app.register_error_handler(MMValidationError, error_handlers.handle_bad_input)
    error_handlers.jsonify_default_exceptions(app)

    cli.auto_register_commands(app, cli)
    app.test_client_class = test_helpers.AuthenticatedClient

    app.register_blueprint(auth.bp)

    app.logger.debug(f"{__name__} service is initialized")
    return app
