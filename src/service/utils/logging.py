import logging
from contextlib import contextmanager


@contextmanager
def disable_logging(highest_level=logging.CRITICAL):
    """
    Temporarily disable all logging on 'highest_level' level and below.
    """
    logging.disable(highest_level)
    try:
        yield
    finally:
        logging.disable(logging.NOTSET)
