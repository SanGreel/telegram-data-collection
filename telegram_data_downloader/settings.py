from pathlib import Path

from decouple import config


BASE_PATH = Path(__file__).resolve().parent


# Telegram API credentials

API_ID = int(config("API_ID", cast=int))

API_HASH = str(config("API_HASH", cast=str))

REACTIONS_LIMIT_PER_MESSAGE = 100

# As Telegram can raise "429 Too Many Requests" error, we need to limit the number of concurrently processed dialogs.
# In case your download is too slow, you can try to increase this number.
CONCURRENT_DIALOG_DOWNLOADS = int(
    config("CONCURRENT_DIALOG_DOWNLOADS", cast=int, default=5)
)


# File export paths

DIALOGS_DATA_FOLDER = Path(
    str(config("DIALOGS_DATA_FOLDER", default=""))
    or BASE_PATH / "data" / "dialogs_data"
).resolve()

DIALOGS_LIST_FOLDER = Path(
    str(config("DIALOGS_LIST_FOLDER", default=""))
    or BASE_PATH / "data" / "dialogs_meta"
).resolve()


# General running settings

LOG_LEVEL = config("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "formatters": {
        "default": {
            "format": "[%(asctime)s] |%(levelname)7s| %(filename)s:%(funcName)s():%(lineno)d: %(message)s",
        },
    },
    "loggers": {
        "telegram_data_downloader": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "asyncio": {
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
