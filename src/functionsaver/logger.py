import logging
from functools import lru_cache


@lru_cache
def get_logger():
    return logging.getLogger("functionsaver")
