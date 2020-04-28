import os

# cannot use relative import because of flask from_pyfile() implementation
from service.config import logging

DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "secret")
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

LOGGING = logging.development
