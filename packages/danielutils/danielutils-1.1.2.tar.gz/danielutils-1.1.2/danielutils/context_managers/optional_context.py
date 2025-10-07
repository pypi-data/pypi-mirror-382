import logging
from typing import ContextManager
from ..logging_.utils import get_logger

logger = get_logger(__name__)


class OptionalContext(ContextManager):
    def __init__(self, predicate: bool, context: ContextManager):
        logger.debug("Initializing OptionalContext with predicate=%s, context=%s", predicate, type(context).__name__)
        self.predicate = predicate
        self.context = context

    def __enter__(self):
        logger.debug("Entering OptionalContext with predicate=%s", self.predicate)
        if self.predicate:
            logger.info("Condition met, entering context: %s", type(self.context).__name__)
            self.context.__enter__()
        else:
            logger.debug("Condition not met, skipping context entry")

    def __exit__(self, __exc_type, __exc_value, __traceback):
        logger.debug("Exiting OptionalContext with predicate=%s, exc_type=%s", self.predicate, __exc_type)
        if self.predicate:
            logger.info("Condition was met, exiting context: %s", type(self.context).__name__)
            self.context.__exit__(__exc_type, __exc_value, __traceback)
        else:
            logger.debug("Condition was not met, no context to exit")


__all__=[
    "OptionalContext"
]