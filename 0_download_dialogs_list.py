import argparse
import logging

from telegram_data_downloader.factory import (
    create_dialog_downloader,
    create_telegram_client,
)

logger = logging.getLogger(__name__)


def init_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download dialogs list for user.")

    parser.add_argument(
        "--dialogs-limit", type=int, help="number of dialogs", required=True
    )
    parser.add_argument("--session-name", type=str, help="session name", default="tmp")

    # read arguments from terminal
    return parser.parse_args()


if __name__ == "__main__":
    args = init_args()

    DIALOGS_LIMIT = args.dialogs_limit
    DIALOGS_LIMIT = DIALOGS_LIMIT if DIALOGS_LIMIT > 0 else None
    SESSION_NAME = args.session_name

    logger.info(f"Downloading dialogs list with {DIALOGS_LIMIT=} and {SESSION_NAME=}")

    telegram_client = create_telegram_client(SESSION_NAME)
    dialog_downloader = create_dialog_downloader(telegram_client)

    # save dialogs
    with telegram_client:
        telegram_client.loop.run_until_complete(
            dialog_downloader.save_dialogs(DIALOGS_LIMIT)
        )

    logger.info("Dialogs list downloaded successfully")
