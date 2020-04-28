from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import ColumnProperty, scoped_session, sessionmaker

from .utils import camel_to_snake_case


class _Meta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        super().__init__(classname, bases, dict_)
        query_expressions = [k for k, v in dict_.items() if is_query_expression(v)]
        if query_expressions:
            fields = [(f, f"_{f}") for f in query_expressions]
            sa.event.listen(cls, "before_update", _build_saver(fields))
            sa.event.listen(cls, "after_update", _build_restorer(fields))


def is_query_expression(value):
    return isinstance(value, ColumnProperty) and value.strategy_key == (
        ("query_expression", True),
    )


def _build_saver(fields):
    def _save(mapper, connection, target):
        for pub, priv in fields:
            value = getattr(target, pub, None)
            if value is not None:
                setattr(target, priv, value)

    return _save


def _build_restorer(fields):
    def _restore(mapper, connection, target):
        for pub, priv in fields:
            value = getattr(target, pub, None)
            if value is None and hasattr(target, priv):
                value = getattr(target, priv)
                setattr(target, pub, value)

    return _restore


class _Base:
    def __init_subclass__(cls, **kwargs):
        cls.__tablename__ = camel_to_snake_case(cls.__name__)


metadata = sa.MetaData(
    naming_convention={
        "all_column_names": lambda constraint, table: "_".join(
            [column.name for column in constraint.columns.values()]
        ),
        "ix": "ix_%(table_name)s__%(all_column_names)s",
        "uq": "uq_%(table_name)s__%(all_column_names)s",
        "ck": "ck_%(table_name)s__%(constraint_name)s",
        "fk": ("fk_%(table_name)s__%(all_column_names)s__%(referred_table_name)s"),
        "pk": "pk_%(table_name)s",
    }
)

session_factory = sessionmaker()
session = scoped_session(session_factory)
Base = declarative_base(metadata=metadata, cls=_Base, metaclass=_Meta)


class TrackModificationTimeMixin:
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


def configure_session(config, bind=None):
    session_options = config.get("SQLALCHEMY_SESSION_OPTIONS", {})
    if not bind:
        bind = create_engine(config)
    session.configure(bind=bind, **session_options)


def create_engine(config):
    database_url = config["SQLALCHEMY_DATABASE_URI"]
    engine_options = config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
    return sa.create_engine(database_url, **engine_options)


def replace(database_url, **kwargs):
    url = make_url(database_url)
    for attr, value in kwargs.items():
        setattr(url, attr, value)
    return str(url)


def truncate_all_tables():
    meta = Base.metadata
    tables = ", ".join('"{}"'.format(table.name) for table in meta.sorted_tables)
    session.execute("TRUNCATE {}".format(tables))
    session.commit()


def create_empty_database(database_url):
    database_url = make_url(database_url)
    dbname = database_url.database
    database_url.database = "postgres"
    engine = sa.create_engine(database_url, isolation_level="AUTOCOMMIT")
    engine.execute("DROP DATABASE IF EXISTS {}".format(dbname))
    engine.execute("CREATE DATABASE {}".format(dbname))


def drop_database(database_url):
    database_url = make_url(database_url)
    dbname = database_url.database
    database_url.database = "postgres"
    engine = sa.create_engine(database_url, isolation_level="AUTOCOMMIT")
    engine.execute("DROP DATABASE {}".format(dbname))


def sequence_next_values(sequence, count):
    """ Get 'count' values from 'sequence' sequence in one sql query"""
    stmt = sa.text("SELECT nextval(:seq) from generate_series(1,:count)")
    stmt = stmt.bindparams(seq=sequence.name, count=count)
    res = session.execute(stmt)
    return [row[0] for row in res.fetchall()]
