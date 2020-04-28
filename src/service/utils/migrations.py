import os
from types import SimpleNamespace

from alembic.config import Config
from alembic.script import ScriptDirectory


def get_alembic_config(rootdir, db_url):
    cmd_options = SimpleNamespace(
        config=os.path.join(rootdir, "alembic.ini"),
        db_url=db_url,
        name="alembic",
        raiseerr=False,
        rev_range=None,
        verbose=False,
        x=None,
    )
    config = Config(file_=cmd_options.config, cmd_opts=cmd_options)
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def get_revisions(rootdir, db_url):
    revisions_dir = ScriptDirectory.from_config(get_alembic_config(rootdir, db_url))
    for revision in revisions_dir.walk_revisions("base", "heads"):
        yield revision


default_test_db_name = "postgresql://postgres:postgres@localhost:5432/test_db"