import textwrap

import migra
import pytest
import sqlalchemy as sa
from alembic.command import downgrade, stamp, upgrade
from sqlbag import S
from sqlbag.sqla import SCOPED_SESSION_MAKERS

from service import create_app
from service.utils import disable_logging
from service.utils.migrations import get_alembic_config
from core.database import Base, create_empty_database, drop_database, replace


@pytest.fixture
def migrations_database():
    app = create_app()
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    database_url = replace(database_url, database="test_migrations")

    with disable_logging():
        create_empty_database(database_url)

    yield database_url

    with disable_logging():
        drop_database(database_url)


@pytest.mark.slow
def test_migrations_stairway(pytestconfig, migrations_database, db_revision):
    """
    Test, that does not require any maintenance - you just add it once to
    check 80% of typos and mistakes in migrations forever.
    Can find forgotten downgrade methods, unremoved data types in downgrade
    methods, typos and many other errors.
    """
    rootdir = pytestconfig.rootdir
    config = get_alembic_config(rootdir, migrations_database)

    upgrade(config, db_revision.revision)
    downgrade(config, db_revision.down_revision or "-1")
    upgrade(config, db_revision.revision)


@pytest.fixture
def two_databases():
    app = create_app()
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    migrations_url = replace(database_url, database="migrations_tdb")
    create_all_url = replace(database_url, database="create_all_tdb")
    with disable_logging():
        create_empty_database(migrations_url)
        create_empty_database(create_all_url)

    yield create_all_url, migrations_url

    # dispose sqlbag engines which has been created internally
    # in order to be able to drop databases
    for session in SCOPED_SESSION_MAKERS.values():
        session.bind.dispose()
    SCOPED_SESSION_MAKERS.clear()

    with disable_logging():
        drop_database(migrations_url)
        drop_database(create_all_url)


@pytest.mark.slow
def test_create_all_and_migrations_produce_same_result(two_databases, pytestconfig):
    """
    Test, that verifies that
    running all migrations from top to bottom
    produces the same result as
    setting the database up from scratch using metadata.create_all()
    """
    create_all_url, migrations_url = two_databases

    create_all_engine = sa.create_engine(create_all_url)
    Base.metadata.create_all(create_all_engine)
    create_all_engine.dispose()
    create_config = get_alembic_config(pytestconfig.rootdir, create_all_url)
    stamp(create_config, "head")

    config = get_alembic_config(pytestconfig.rootdir, migrations_url)
    upgrade(config, "head")

    with S(migrations_url) as s_migrations, S(create_all_url) as s_create_all:
        m = migra.Migration(s_migrations, s_create_all)
        m.set_safety(False)
        m.add_all_changes()
        if m.statements:
            sql = m.sql.strip().replace("\n\n", "\n")
            sql = textwrap.indent(sql, 4 * " ")
            pytest.fail(fail_message.format(sql))


fail_message = """
Running all migrations from top to bottom and metadata.create_all()
produce different database schema. Following actions are required
to turn `migrations` schema into `create_all` schema:
{}
"""
