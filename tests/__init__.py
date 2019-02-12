import os
import logging


def configure_logging():
    level_str = os.getenv('UNIT_TESTS_LOG_LEVEL') or 'INFO'
    try:
        level = logging.__dict__[level_str]
    except KeyError:
        level = logging.INFO
    logging.basicConfig(level=level)

