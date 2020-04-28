import os

# cannot use relative import because of flask from_pyfile() implementation
from service.config import logging
from service.utils.migrations import default_test_db_name

TESTING = True
SERVER_NAME = "service.loc"
SECRET_KEY = os.environ.get("SECRET_KEY", "secret")
SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", default_test_db_name)
LOGGING = logging.testing
