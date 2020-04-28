import os


def choose_config():
    environment = os.environ.get("FLASK_ENV", "development")
    return "config/{}.py".format(environment)
