import logging

import telethon

from . import settings
from .loader.json import JSONDialogReaderWriter
from .loader.csv import CSVMessageWriter
from .processor.dialog_downloader import DialogDownloader
from .processor.message_downloader import MessageDownloader


logger = logging.getLogger(__name__)


def create_telegram_client(session_name: str) -> telethon.TelegramClient:
    logger.debug("creating telegram client...")
    return telethon.TelegramClient(
        session_name,
        settings.API_ID,
        settings.API_HASH,
        system_version=settings.CLIENT_SYSTEM_VERSION,
    )


def create_json_dialog_reader_writer() -> JSONDialogReaderWriter:
    return JSONDialogReaderWriter(settings.DIALOGS_LIST_FOLDER)


def create_csv_message_saver() -> CSVMessageWriter:
    return CSVMessageWriter(settings.DIALOGS_DATA_FOLDER)


def create_dialog_downloader(
    telegram_client: telethon.TelegramClient,
) -> DialogDownloader:
    logger.debug("creating dialog downloader...")
    return DialogDownloader(telegram_client, create_json_dialog_reader_writer())


def create_message_downloader(
    telegram_client: telethon.TelegramClient,
) -> MessageDownloader:
    logger.debug("creating message downloader...")
    downloader = MessageDownloader(
        telegram_client,
        create_json_dialog_reader_writer(),
        create_csv_message_saver(),
        reactions_limit_per_message=settings.REACTIONS_LIMIT_PER_MESSAGE,
    )
    downloader.concurrent_dialog_downloads = settings.CONCURRENT_DIALOG_DOWNLOADS
    return downloader
