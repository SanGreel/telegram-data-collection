from pathlib import Path

from decouple import config


BASE_PATH = Path(__file__).resolve().parent


# Telegram API Settings

API_ID = int(config("API_ID", cast=int))

API_HASH = str(config("API_HASH", cast=str))

CLIENT_SYSTEM_VERSION = "4.16.30-vxCUSTOM"


# As Telegram can raise "429 Too Many Requests" error, we need to limit the number of
# concurrently processed dialogs. In case your download is too slow, you can try to
# increase this number.
CONCURRENT_DIALOG_DOWNLOADS = int(
    config("CONCURRENT_DIALOG_DOWNLOADS", cast=int, default=5)
)

# Number of reactions to download per message.
REACTIONS_LIMIT_PER_MESSAGE: int = int(
    config("REACTIONS_LIMIT_PER_MESSAGE", cast=int, default=100)
)

# Reaction fetching can sometimes fail due to Telegram API limitations.
# If download script still says about timeout, try to increase these values.
MESSAGE_REACTION_EXPONENTIAL_BACKOFF_SLEEP_TIME = float(
    config("MESSAGE_REACTION_EXPONENTIAL_BACKOFF_SLEEP_TIME", cast=float, default=5.0)
)

MESSAGE_REACTION_EXPONENTIAL_BACKOFF_MAX_TRIES = int(
    config("MESSAGE_REACTION_EXPONENTIAL_BACKOFF_MAX_TRIES", cast=int, default=5)
)


# https://core.telegram.org/api/takeout
# Options for the takeout method.
# For basic usage, should be left as is.
CLIENT_TAKEOUT_FINALIZE: bool = True

CLIENT_TAKEOUT_FETCH_CONTACTS: bool = False

CLIENT_TAKEOUT_FETCH_USERS: bool = True

CLIENT_TAKEOUT_FETCH_GROUPS: bool = True

CLIENT_TAKEOUT_FETCH_MEGAGROUPS: bool = True

CLIENT_TAKEOUT_FETCH_CHANNELS: bool = True

CLIENT_TAKEOUT_FETCH_FILES: bool = False


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
