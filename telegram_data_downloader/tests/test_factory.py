import pytest
from unittest.mock import patch, MagicMock

from telegram_data_downloader.factory import (
    create_telegram_client,
    create_json_dialog_reader_writer,
    create_csv_message_saver,
    create_dialog_downloader,
    create_message_downloader,
)
from telegram_data_downloader.processor.dialog_downloader import DialogDownloader
from telegram_data_downloader.processor.message_downloader import MessageDownloader


@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to mock settings."""
    monkeypatch.setattr("telegram_data_downloader.settings.API_ID", 123456)
    monkeypatch.setattr("telegram_data_downloader.settings.API_HASH", "test_hash")
    monkeypatch.setattr(
        "telegram_data_downloader.settings.CLIENT_SYSTEM_VERSION", "test_version"
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.DIALOGS_LIST_FOLDER", "dialogs_meta"
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.DIALOGS_DATA_FOLDER", "dialogs_data"
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.REACTIONS_LIMIT_PER_MESSAGE", 10
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.CONCURRENT_DIALOG_DOWNLOADS", 5
    )


def test_create_telegram_client_fixture(mock_settings):
    """
    Test creating a Telegram client.
    """
    with patch("telethon.TelegramClient") as mock_client:
        client = create_telegram_client("test_session")
        mock_client.assert_called_with(
            "test_session",
            123456,
            "test_hash",
            system_version="test_version",
        )
        assert client == mock_client.return_value


def test_create_json_dialog_reader_writer_fixture(mock_settings):
    """
    Test creating a JSON dialog reader/writer.
    """
    with patch(
        "telegram_data_downloader.factory.JSONDialogReaderWriter"
    ) as mock_reader_writer:
        reader_writer_instance = MagicMock()
        mock_reader_writer.return_value = reader_writer_instance
        reader_writer = create_json_dialog_reader_writer()
        mock_reader_writer.assert_called_once_with("dialogs_meta")
        assert reader_writer == mock_reader_writer.return_value


def test_create_csv_message_saver_fixture(mock_settings):
    """
    Test creating a CSV message saver.
    """
    with patch("telegram_data_downloader.factory.CSVMessageWriter") as mock_csv_writer:
        csv_writer_instance = MagicMock()
        mock_csv_writer.return_value = csv_writer_instance
        csv_writer = create_csv_message_saver()
        mock_csv_writer.assert_called_once_with("dialogs_data")
        assert csv_writer == mock_csv_writer.return_value


def test_create_dialog_downloader_fixture(mock_settings):
    """
    Test creating a dialog downloader.
    """
    mock_client = MagicMock()
    with patch(
        "telegram_data_downloader.factory.create_json_dialog_reader_writer"
    ) as mock_reader_writer:
        mock_reader_writer.return_value = MagicMock()
        downloader = create_dialog_downloader(mock_client)
        assert isinstance(downloader, DialogDownloader)
        assert downloader.client == mock_client
        mock_reader_writer.assert_called_once()


def test_create_message_downloader_fixture(mock_settings):
    """
    Test creating a message downloader.
    """
    mock_client = MagicMock()
    with (
        patch(
            "telegram_data_downloader.factory.create_json_dialog_reader_writer"
        ) as mock_reader_writer,
        patch(
            "telegram_data_downloader.factory.create_csv_message_saver"
        ) as mock_message_saver,
    ):
        mock_reader_writer.return_value = MagicMock()
        mock_message_saver.return_value = MagicMock()
        downloader = create_message_downloader(mock_client)
        assert isinstance(downloader, MessageDownloader)
        assert downloader.client == mock_client
        assert downloader.dialog_reader == mock_reader_writer.return_value
        assert downloader.message_writer == mock_message_saver.return_value
        assert downloader.reactions_limit_per_message == 10
        assert downloader.concurrent_dialog_downloads == 5
