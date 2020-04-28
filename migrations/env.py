from alembic import context

from service import create_app
from core.database import Base

config = context.config


target_metadata = Base.metadata
app_config = create_app().config
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", app_config["SQLALCHEMY_DATABASE_URI"])
