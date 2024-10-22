import logging
import logging.config

from . import settings


logging.config.dictConfig(settings.LOGGING)
