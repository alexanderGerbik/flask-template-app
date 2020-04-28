import os

import pytest
from sqlalchemy import event

from service import create_app
from service.utils import disable_logging
from service.utils.migrations import get_revisions, default_test_db_name
from core.database import (
    Base,
    configure_session,
    create_empty_database,
    create_engine,
    drop_database,
    session,
)


@pytest.fixture(scope="session", autouse=True)
def set_environ():
    os.environ["FLASK_ENV"] = "testing"


@pytest.fixture(scope="session")
def _database():
    app = create_app()
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    with disable_logging():
        create_empty_database(database_url)
        engine = create_engine(app.config)
        Base.metadata.create_all(engine)

    yield app.config, engine

    with disable_logging():
        engine.dispose()
        drop_database(database_url)


def _restart_savepoint(s, transaction):
    if transaction.nested and not transaction._parent.nested:
        s.begin_nested()


def _error_out():
    message = "Apply `@pytest.mark.allow_db_rollback` in order to use db rollbacks"
    raise RuntimeError(message)


@pytest.fixture
def database(_database, request):
    config, engine = _database
    connection = engine.connect()
    trans = connection.begin()
    configure_session(config, bind=connection)

    if request.node.get_closest_marker("allow_db_rollback"):
        session.begin_nested()
        event.listens_for(session, "after_transaction_end")(_restart_savepoint)
    else:
        session().rollback = _error_out

    yield

    session.remove()
    trans.rollback()
    connection.close()


@pytest.fixture
def config():
    return {}


@pytest.fixture
def app(database, config):
    app = create_app(config)
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    client = app.test_client()
    with client:
        yield client


@pytest.fixture
def request_context(app):
    with app.test_request_context("/"):
        app.preprocess_request()
        yield


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line(
        "markers", "allow_db_rollback: allow database rollback in test"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-slow"):
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_generate_tests(metafunc):
    if "db_revision" in metafunc.fixturenames:
        rootdir = metafunc.config.rootdir
        database_url = os.environ.get("TEST_DATABASE_URL", default_test_db_name)
        revisions = list(get_revisions(rootdir, database_url))
        params = [pytest.param(r, id=r.revision) for r in revisions]
        metafunc.parametrize("db_revision", params)
