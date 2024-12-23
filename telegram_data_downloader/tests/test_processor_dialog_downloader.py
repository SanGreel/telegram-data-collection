import pytest
import telethon.errors

from unittest.mock import AsyncMock, MagicMock
from telegram_data_downloader.processor.dialog_downloader import DialogDownloader
from telegram_data_downloader.dict_types.dialog import DialogType, DialogMemberData


class MockRPCError(telethon.errors.RPCError):
    """Mock class for RPC errors."""

    def __init__(self, message, request=None):
        super().__init__(message=message, request=request)


@pytest.mark.asyncio
async def test_save_dialogs_with_limit():
    """
    Test the save_dialogs method with a specified limit.
    Ensures that only the limited number of dialogs are processed and saved.
    """
    # Arrange
    mock_client = MagicMock()
    # Create two dialogs instead of three to match the limit
    dialog1 = MagicMock()
    dialog1.id = 1
    dialog1.name = "Dialog1"
    dialog1.is_user = True
    dialog1.is_group = False
    dialog1.is_channel = False

    dialog2 = MagicMock()
    dialog2.id = 2
    dialog2.name = "Dialog2"
    dialog2.is_user = False
    dialog2.is_group = True
    dialog2.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog1, dialog2])
    mock_client.get_participants = AsyncMock(return_value=[])

    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(2)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=2)
    assert mock_client.get_participants.await_count == 2
    assert mock_writer.write_dialog.call_count == 2

    # Verify first dialog
    first_call_args = mock_writer.write_dialog.call_args_list[0][0][0]
    assert first_call_args["id"] == 1
    assert first_call_args["name"] == "Dialog1"
    assert first_call_args["type"] == DialogType.PRIVATE
    assert first_call_args["users"] == []

    # Verify second dialog
    second_call_args = mock_writer.write_dialog.call_args_list[1][0][0]
    assert second_call_args["id"] == 2
    assert second_call_args["name"] == "Dialog2"
    assert second_call_args["type"] == DialogType.GROUP
    assert second_call_args["users"] == []


@pytest.mark.asyncio
async def test_save_dialogs_without_limit():
    """
    Test the save_dialogs method without specifying a limit.
    Ensures that all available dialogs are processed and saved.
    """
    # Arrange
    mock_client = MagicMock()
    dialog1 = MagicMock()
    dialog1.id = 1
    dialog1.name = "Dialog1"
    dialog1.is_user = True
    dialog1.is_group = False
    dialog1.is_channel = False

    dialog2 = MagicMock()
    dialog2.id = 2
    dialog2.name = "Dialog2"
    dialog2.is_user = False
    dialog2.is_group = True
    dialog2.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog1, dialog2])
    mock_client.get_participants = AsyncMock(return_value=[])

    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(None)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=None)
    assert mock_client.get_participants.await_count == 2
    assert mock_writer.write_dialog.call_count == 2


@pytest.mark.asyncio
async def test_save_dialog_with_participants():
    """
    Test the _save_dialog method to ensure that participants are correctly retrieved and saved.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 1
    dialog.name = "Dialog1"
    dialog.is_user = True
    dialog.is_group = False
    dialog.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog])
    mock_client.get_participants = AsyncMock(
        return_value=[
            MagicMock(
                id=10,
                first_name="User1",
                last_name="Last1",
                username="user1",
                phone=None,
            ),
            MagicMock(
                id=20,
                first_name="User2",
                last_name=None,
                username="user2",
                phone="123456789",
            ),
        ]
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(1)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=1)
    mock_client.get_participants.assert_awaited_once_with(dialog)
    mock_writer.write_dialog.assert_called_once()

    dialog_metadata = mock_writer.write_dialog.call_args[0][0]
    assert dialog_metadata["id"] == 1
    assert dialog_metadata["name"] == "Dialog1"
    assert dialog_metadata["type"] == DialogType.PRIVATE
    assert dialog_metadata["users"] == [
        DialogMemberData(
            user_id=10,
            first_name="User1",
            last_name="Last1",
            username="user1",
            phone=None,
        ),
        DialogMemberData(
            user_id=20,
            first_name="User2",
            last_name=None,
            username="user2",
            phone="123456789",
        ),
    ]


@pytest.mark.asyncio
async def test_save_dialog_unknown_type():
    """
    Test the _save_dialog method with a dialog type that is not private, group, or channel.
    Ensures that the dialog type is set to UNKNOWN.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 99
    dialog.name = "UnknownDialog"
    dialog.is_user = False
    dialog.is_group = False
    dialog.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog])
    mock_client.get_participants = AsyncMock(return_value=[])
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(1)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=1)
    mock_client.get_participants.assert_awaited_once_with(dialog)
    mock_writer.write_dialog.assert_called_once()

    dialog_metadata = mock_writer.write_dialog.call_args[0][0]
    assert dialog_metadata["id"] == 99
    assert dialog_metadata["name"] == "UnknownDialog"
    assert dialog_metadata["type"] == DialogType.UNKNOWN
    assert dialog_metadata["users"] == []


@pytest.mark.asyncio
async def test_save_dialog_participants_chat_admin_required():
    """
    Test the _save_dialog method when a ChatAdminRequiredError is raised during participant retrieval.
    Ensures that the dialog is saved without users.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 2
    dialog.name = "AdminRequiredDialog"
    dialog.is_user = False
    dialog.is_group = True
    dialog.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog])
    mock_client.get_participants = AsyncMock(
        side_effect=telethon.errors.ChatAdminRequiredError(request="test_request")
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(1)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=1)
    mock_client.get_participants.assert_awaited_once_with(dialog)
    mock_writer.write_dialog.assert_called_once()

    dialog_metadata = mock_writer.write_dialog.call_args[0][0]
    assert dialog_metadata["id"] == 2
    assert dialog_metadata["name"] == "AdminRequiredDialog"
    assert dialog_metadata["type"] == DialogType.GROUP
    assert dialog_metadata["users"] == []


@pytest.mark.asyncio
async def test_save_dialog_participants_channel_private_error():
    """
    Test the _save_dialog method when a ChannelPrivateError is raised during participant retrieval.
    Ensures that the dialog is saved without users.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 3
    dialog.name = "PrivateChannel"
    dialog.is_user = False
    dialog.is_group = False
    dialog.is_channel = True

    mock_client.get_dialogs = AsyncMock(return_value=[dialog])
    mock_client.get_participants = AsyncMock(
        side_effect=telethon.errors.ChannelPrivateError(request="test_request")
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(1)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=1)
    mock_client.get_participants.assert_awaited_once_with(dialog)
    mock_writer.write_dialog.assert_called_once()

    dialog_metadata = mock_writer.write_dialog.call_args[0][0]
    assert dialog_metadata["id"] == 3
    assert dialog_metadata["name"] == "PrivateChannel"
    assert dialog_metadata["type"] == DialogType.CHANNEL
    assert dialog_metadata["users"] == []


@pytest.mark.asyncio
async def test_save_dialog_participants_channel_invalid_error():
    """
    Test the _save_dialog method when a ChannelInvalidError is raised during participant retrieval.
    Ensures that the dialog is saved without users.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 4
    dialog.name = "InvalidChannel"
    dialog.is_user = False
    dialog.is_group = False
    dialog.is_channel = True

    mock_client.get_dialogs = AsyncMock(return_value=[dialog])
    mock_client.get_participants = AsyncMock(
        side_effect=telethon.errors.ChannelInvalidError(request="test_request")
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(1)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=1)
    mock_client.get_participants.assert_awaited_once_with(dialog)
    mock_writer.write_dialog.assert_called_once()

    dialog_metadata = mock_writer.write_dialog.call_args[0][0]
    assert dialog_metadata["id"] == 4
    assert dialog_metadata["name"] == "InvalidChannel"
    assert dialog_metadata["type"] == DialogType.CHANNEL
    assert dialog_metadata["users"] == []


@pytest.mark.asyncio
async def test_save_dialog_participants_unknown_rpc_error():
    """
    Test the _save_dialog method when an unknown RPCError is raised during participant retrieval.
    Ensures that the dialog is saved without users.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 5
    dialog.name = "UnknownErrorDialog"
    dialog.is_user = False
    dialog.is_group = True
    dialog.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog])
    mock_client.get_participants = AsyncMock(
        side_effect=MockRPCError("Unknown RPC Error", request="test_request")
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(1)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=1)
    mock_client.get_participants.assert_awaited_once_with(dialog)
    mock_writer.write_dialog.assert_called_once()

    dialog_metadata = mock_writer.write_dialog.call_args[0][0]
    assert dialog_metadata["id"] == 5
    assert dialog_metadata["name"] == "UnknownErrorDialog"
    assert dialog_metadata["type"] == DialogType.GROUP
    assert dialog_metadata["users"] == []


@pytest.mark.asyncio
async def test_save_dialogs_no_dialogs():
    """
    Test the save_dialogs method when no dialogs are returned.
    Ensures that the method handles empty dialog lists gracefully.
    """
    # Arrange
    mock_client = MagicMock()
    mock_client.get_dialogs = AsyncMock(return_value=[])
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(None)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=None)
    mock_client.get_participants.assert_not_called()
    mock_writer.write_dialog.assert_not_called()


@pytest.mark.asyncio
async def test_save_dialogs_multiple_dialogs():
    """
    Test the save_dialogs method with multiple dialogs of different types and participant data.
    Ensures that all dialogs are processed correctly.
    """
    # Arrange
    mock_client = MagicMock()
    dialog1 = MagicMock()
    dialog1.id = 1
    dialog1.name = "Dialog1"
    dialog1.is_user = True
    dialog1.is_group = False
    dialog1.is_channel = False

    dialog2 = MagicMock()
    dialog2.id = 2
    dialog2.name = "Dialog2"
    dialog2.is_user = False
    dialog2.is_group = True
    dialog2.is_channel = False

    dialog3 = MagicMock()
    dialog3.id = 3
    dialog3.name = "Dialog3"
    dialog3.is_user = False
    dialog3.is_group = False
    dialog3.is_channel = True

    mock_client.get_dialogs = AsyncMock(return_value=[dialog1, dialog2, dialog3])
    mock_client.get_participants = AsyncMock(
        side_effect=[
            [],  # Dialog1 has no participants
            [
                MagicMock(
                    id=20,
                    first_name="User2",
                    last_name="Last2",
                    username="user2",
                    phone="123456789",
                )
            ],  # Dialog2 has one participant
            [],  # Dialog3 has no participants
        ]
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(None)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=None)
    assert mock_client.get_participants.await_count == 3
    assert mock_writer.write_dialog.call_count == 3

    # Verify Dialog1
    dialog1_metadata = mock_writer.write_dialog.call_args_list[0][0][0]
    assert dialog1_metadata["id"] == 1
    assert dialog1_metadata["name"] == "Dialog1"
    assert dialog1_metadata["type"] == DialogType.PRIVATE
    assert dialog1_metadata["users"] == []

    # Verify Dialog2
    dialog2_metadata = mock_writer.write_dialog.call_args_list[1][0][0]
    assert dialog2_metadata["id"] == 2
    assert dialog2_metadata["name"] == "Dialog2"
    assert dialog2_metadata["type"] == DialogType.GROUP
    assert dialog2_metadata["users"] == [
        DialogMemberData(
            user_id=20,
            first_name="User2",
            last_name="Last2",
            username="user2",
            phone="123456789",
        )
    ]

    # Verify Dialog3
    dialog3_metadata = mock_writer.write_dialog.call_args_list[2][0][0]
    assert dialog3_metadata["id"] == 3
    assert dialog3_metadata["name"] == "Dialog3"
    assert dialog3_metadata["type"] == DialogType.CHANNEL
    assert dialog3_metadata["users"] == []


@pytest.mark.asyncio
async def test_save_dialogs_duplicate_dialogs():
    """
    Test the save_dialogs method with duplicate dialogs to ensure that each dialog is processed independently.
    """
    # Arrange
    mock_client = MagicMock()
    dialog = MagicMock()
    dialog.id = 1
    dialog.name = "DuplicateDialog"
    dialog.is_user = True
    dialog.is_group = False
    dialog.is_channel = False

    mock_client.get_dialogs = AsyncMock(return_value=[dialog, dialog])
    mock_client.get_participants = AsyncMock(return_value=[])
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act
    result = await downloader.save_dialogs(2)

    # Assert
    assert result is True
    mock_client.get_dialogs.assert_awaited_once_with(limit=2)
    assert mock_client.get_participants.await_count == 2
    assert mock_writer.write_dialog.call_count == 2

    # Both dialogs should have the same data
    first_call = mock_writer.write_dialog.call_args_list[0][0][0]
    second_call = mock_writer.write_dialog.call_args_list[1][0][0]
    assert first_call == second_call
    assert first_call["id"] == 1
    assert first_call["name"] == "DuplicateDialog"
    assert first_call["type"] == DialogType.PRIVATE
    assert first_call["users"] == []


@pytest.mark.asyncio
async def test_save_dialogs_exception_in_get_dialogs():
    """
    Test the save_dialogs method when an exception occurs during get_dialogs.
    Ensures that the exception is propagated.
    """
    # Arrange
    mock_client = MagicMock()
    mock_client.get_dialogs = AsyncMock(
        side_effect=MockRPCError("GetDialogs RPC Error", request="test_request")
    )
    mock_writer = MagicMock()
    downloader = DialogDownloader(mock_client, mock_writer)

    # Act & Assert
    with pytest.raises(telethon.errors.RPCError) as exc_info:
        await downloader.save_dialogs(1)
    assert exc_info.value.message == "GetDialogs RPC Error"
