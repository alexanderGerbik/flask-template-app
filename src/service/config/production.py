import os

# cannot use relative import because of flask from_pyfile() implementation
from service.config import logging

# intentionally using [] here to fail early if "SECRET_KEY" env variable is not set
SECRET_KEY = os.environ["SECRET_KEY"]
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

LOGGING = logging.production
