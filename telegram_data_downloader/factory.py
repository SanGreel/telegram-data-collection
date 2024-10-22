import telethon

from . import settings
from .loader.json import JSONDialogWriter
from .processor.downloader import DialogDownloader


def create_telegram_client(session_name: str) -> telethon.TelegramClient:
    return telethon.TelegramClient(
        session_name,
        settings.API_ID,
        settings.API_HASH,
        system_version="4.16.30-vxCUSTOM",
    )


def create_json_dialog_saver() -> JSONDialogWriter:
    return JSONDialogWriter(settings.DIALOGS_LIST_FOLDER)


def create_dialog_downloader(
    telegram_client: telethon.TelegramClient,
) -> DialogDownloader:
    return DialogDownloader(telegram_client, create_json_dialog_saver())
