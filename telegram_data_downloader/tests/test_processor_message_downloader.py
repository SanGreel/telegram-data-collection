import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime

import telethon.errors
from telethon.tl import types as tl_types

from telegram_data_downloader.processor.message_downloader import MessageDownloader
from telegram_data_downloader.dict_types.dialog import DialogMetadata, DialogType
from telegram_data_downloader.dict_types.message import MessageType, PeerID


class MockRPCError(telethon.errors.RPCError):
    def __init__(self, message, request=None):
        super().__init__(message=message, request=request)


@pytest.fixture
def mock_settings(monkeypatch):
    """
    Mock the settings used in MessageDownloader.
    """
    monkeypatch.setattr(
        "telegram_data_downloader.settings.REACTIONS_LIMIT_PER_MESSAGE", 10
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.CONCURRENT_DIALOG_DOWNLOADS", 5
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.MESSAGE_REACTION_EXPONENTIAL_BACKOFF_SLEEP_TIME",
        0.1,
    )
    monkeypatch.setattr(
        "telegram_data_downloader.settings.MESSAGE_REACTION_EXPONENTIAL_BACKOFF_MAX_TRIES",
        3,
    )


@pytest.mark.asyncio
async def test_reformat_message_photo():
    """
    Test the _reformat_message method with a photo message.
    """
    mock_client = MagicMock()
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    photo_media = MagicMock()
    photo_media.__class__ = tl_types.MessageMediaPhoto

    message = MagicMock()
    message.id = 105
    message.date = datetime(2024, 1, 5, 0, 0, 0)
    message.from_id = PeerID(5)
    message.fwd_from = None
    message.message = ""
    message.media = photo_media
    message.to_id = PeerID(6)

    formatted_message = downloader._reformat_message(message)

    assert formatted_message == {
        "id": 105,
        "date": datetime(2024, 1, 5, 0, 0, 0),
        "from_id": PeerID(5),
        "fwd_from": None,
        "message": "",
        "type": MessageType.PHOTO,
        "duration": None,
        "to_id": PeerID(6),
        "reactions": {},
    }


@pytest.mark.asyncio
async def test_reformat_message_voice():
    """
    Test the _reformat_message method with a voice message.
    """
    mock_client = MagicMock()
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    audio_attr = tl_types.DocumentAttributeAudio(duration=30, voice=True)
    media_document = MagicMock()
    media_document.attributes = [audio_attr]
    media_document.__class__ = tl_types.Document

    media = MagicMock()
    media.document = media_document
    media.__class__ = tl_types.MessageMediaDocument

    message = MagicMock()
    message.id = 108
    message.date = datetime(2024, 1, 8, 0, 0, 0)
    message.from_id = PeerID(11)
    message.fwd_from = None
    message.message = ""
    message.media = media
    message.to_id = PeerID(12)

    formatted_message = downloader._reformat_message(message)

    assert formatted_message == {
        "id": 108,
        "date": datetime(2024, 1, 8, 0, 0, 0),
        "from_id": PeerID(11),
        "fwd_from": None,
        "message": "",
        "type": MessageType.VOICE,
        "duration": 30,
        "to_id": PeerID(12),
        "reactions": {},
    }


@pytest.mark.asyncio
async def test_reformat_message_sticker():
    """
    Test the _reformat_message method with a sticker message.
    """
    mock_client = MagicMock()
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    # Correctly initialize DocumentAttributeSticker with 'stickerset'
    stickerset = tl_types.InputStickerSetID(id=12345, access_hash=67890)
    sticker_attr = tl_types.DocumentAttributeSticker(
        stickerset=stickerset, alt="Cool Sticker"
    )
    media_document = MagicMock()
    media_document.attributes = [sticker_attr]
    media_document.__class__ = tl_types.Document

    media = MagicMock()
    media.document = media_document
    media.__class__ = tl_types.MessageMediaDocument

    message = MagicMock()
    message.id = 110
    message.date = datetime(2024, 1, 10, 0, 0, 0)
    message.from_id = PeerID(13)
    message.fwd_from = None
    message.message = ""
    message.media = media
    message.to_id = PeerID(14)

    formatted_message = downloader._reformat_message(message)

    assert formatted_message == {
        "id": 110,
        "date": datetime(2024, 1, 10, 0, 0, 0),
        "from_id": PeerID(13),
        "fwd_from": None,
        "message": "Cool Sticker",
        "type": MessageType.STICKER,
        "duration": None,
        "to_id": PeerID(14),
        "reactions": {},
    }


@pytest.mark.asyncio
async def test_reformat_message_video():
    """
    Test the _reformat_message method with a video message.
    """
    mock_client = MagicMock()
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    # Correctly initialize DocumentAttributeVideo with 'duration', 'w', and 'h'
    video_attr = tl_types.DocumentAttributeVideo(duration=120, w=640, h=480)
    media_document = MagicMock()
    media_document.attributes = [video_attr]
    media_document.__class__ = tl_types.Document

    media = MagicMock()
    media.document = media_document
    media.__class__ = tl_types.MessageMediaDocument

    message = MagicMock()
    message.id = 115
    message.date = datetime(2024, 1, 15, 0, 0, 0)
    message.from_id = PeerID(15)
    message.fwd_from = None
    message.message = ""
    message.media = media
    message.to_id = PeerID(16)

    formatted_message = downloader._reformat_message(message)

    assert formatted_message == {
        "id": 115,
        "date": datetime(2024, 1, 15, 0, 0, 0),
        "from_id": PeerID(15),
        "fwd_from": None,
        "message": "",
        "type": MessageType.VIDEO,
        "duration": 120,
        "to_id": PeerID(16),
        "reactions": {},
    }


@pytest.mark.asyncio
async def test_get_message_iterator_entity_not_found(mock_settings):
    """
    Test the _get_message_iterator method when the dialog entity cannot be found.
    Ensures that no messages are yielded.
    """
    mock_client = MagicMock()
    mock_client.get_entity = AsyncMock(side_effect=ValueError("Entity not found"))
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    dialog = DialogMetadata(
        id=2, name="Invalid Dialog", type=DialogType.PRIVATE, users=[]
    )
    msg_limit = 5

    with patch.object(downloader.dialog_reader, "read_dialog", return_value=dialog):
        message_iterator = downloader._get_message_iterator(dialog, msg_limit)
        messages = []
        async for msg in message_iterator:
            messages.append(msg)

    assert len(messages) == 0
    

@pytest.mark.asyncio
async def test_get_message_iterator_private_dialog_without_username(mock_settings):
    """
    Test the _get_message_iterator method for a private dialog without username.
    Should raise ValueError.
    """
    mock_client = MagicMock()
    mock_client.get_entity = AsyncMock(side_effect=ValueError("Entity not found"))
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    dialog = DialogMetadata(
        id=4,
        name="Private Dialog No Username",
        type=DialogType.PRIVATE,
        users=[
            {
                "user_id": 40,
                "first_name": "User",
                "last_name": "Forty",
                "username": None,
                "phone": None,
            }
        ],
    )
    msg_limit = 10

    with patch.object(downloader.dialog_reader, "read_dialog", return_value=dialog):
        with pytest.raises(ValueError, match="username is empty"):
            message_iterator = downloader._get_message_iterator(dialog, msg_limit)
            async for msg in message_iterator:
                pass
    

@pytest.mark.asyncio
async def test_download_dialog_successful(mock_settings):
    """
    Test the download_dialogs method for successful download of dialogs.
    """
    mock_client = MagicMock()
    mock_dialog_reader = MagicMock()
    mock_message_writer = MagicMock()

    downloader = MessageDownloader(
        client=mock_client,
        dialog_reader=mock_dialog_reader,
        message_writer=mock_message_writer,
        reactions_limit_per_message=10,
    )

    dialog1 = DialogMetadata(id=1, name="Dialog1", type=DialogType.PRIVATE, users=[])
    dialog2 = DialogMetadata(id=2, name="Dialog2", type=DialogType.GROUP, users=[])

    async def mock_download_dialog(dialog, msg_limit):
        # Simulate message downloading
        return

    downloader._download_dialog = AsyncMock(side_effect=mock_download_dialog)

    await downloader.download_dialogs([dialog1, dialog2], msg_limit=100)

    assert downloader._download_dialog.await_count == 2
    downloader._download_dialog.assert_has_awaits(
        [
            call(dialog1, 100),
            call(dialog2, 100),
        ]
    )