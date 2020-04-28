from copy import deepcopy

production = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"},
        "sql": {"format": "[%(asctime)s] %(message)s"},
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
        }
    },
    "loggers": {"service": {"level": "INFO"}},
    "root": {"level": "INFO", "handlers": ["wsgi"]},
}

development = deepcopy(production)
# log sql queries
development["handlers"]["sql"] = {
    "class": "logging.StreamHandler",
    "stream": "ext://sys.stdout",
    "formatter": "sql",
}
development["loggers"]["sqlalchemy.engine.base.Engine"] = {
    "propagate": False,
    "level": "INFO",
    "handlers": ["sql"],
}

testing = deepcopy(production)
testing["root"]["handlers"] = []
