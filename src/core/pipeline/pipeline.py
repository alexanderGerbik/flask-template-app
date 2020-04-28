import logging
from contextlib import contextmanager


from core.database import session

from .registry import Registry


class Pipeline(Registry):
    def __init__(self, user):
        self.logger = self._get_logger(user)


    @classmethod
    def create(cls, user):
        return super()._create(user.type, user)

    def _get_logger(self, user):
        logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        adapter = PipelineLoggerAdapter(logger, user)
        return adapter


@contextmanager
def locked_and_refreshed(instance):
    model = instance.__class__
    session.commit()
    session.query(model.id).filter(model.id == instance.id).with_for_update().one()
    session.refresh(instance)
    try:
        yield
    finally:
        session.commit()


class PipelineLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, user):
        super().__init__(logger, {})
        self.prefix = f"[user_id={user.id}]"

    def process(self, msg, kwargs):
        return f"{self.prefix} {msg}", kwargs
