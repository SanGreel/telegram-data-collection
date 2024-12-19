import json
import pytest

from telegram_data_downloader.dict_types.dialog import DialogMetadata, DialogType, DialogMemberData
from telegram_data_downloader.loader.json import JSONDialogReaderWriter


class TestWriteDialog:
    @pytest.mark.parametrize("dialog_type", list(DialogType))
    def test_with_users(self, tmp_path, dialog_type):
        # Arrange
        dialog_id = 1
        dialog = DialogMetadata(
            id=dialog_id,
            name="str",
            type=dialog_type,
            users=[
                DialogMemberData(
                    user_id=1,
                    first_name="str",
                    last_name="str",
                    username="str",
                    phone="str",
                ),
                DialogMemberData(
                    user_id=2,
                    first_name="str",
                    last_name="str",
                    username="str",
                    phone="str",
                ),
            ],
        )
        reader = JSONDialogReaderWriter(tmp_path)
        # Act
        reader.write_dialog(dialog)
        # Assert
        with open(tmp_path / f"{dialog_id}.json", encoding="utf-8") as f:
            data = json.load(f)
        assert data == dict(dialog) | {"type": dialog_type.value}

    @pytest.mark.parametrize("dialog_type", list(DialogType))
    def test_no_users(self, tmp_path, dialog_type):
        # Arrange
        dialog_id = 1
        dialog = DialogMetadata(id=dialog_id, name="str", type=dialog_type, users=[])
        reader = JSONDialogReaderWriter(tmp_path)
        # Act
        reader.write_dialog(dialog)
        # Assert
        with open(tmp_path / f"{dialog_id}.json", encoding="utf-8") as f:
            data = json.load(f)
        assert data == dict(dialog) | {"type": dialog_type.value}


class TestReadDialog:
    @pytest.mark.parametrize("dialog_type", list(DialogType))
    def test_with_users(self, tmp_path, dialog_type):
        # Arrange
        dialog_id = 1
        dialog = DialogMetadata(
            id=dialog_id,
            name="str",
            type=dialog_type,
            users=[
                DialogMemberData(
                    user_id=1,
                    first_name="str",
                    last_name="str",
                    username="str",
                    phone="str",
                ),
                DialogMemberData(
                    user_id=2,
                    first_name="str",
                    last_name="str",
                    username="str",
                    phone="str",
                ),
            ],
        )
        with open(tmp_path / f"{dialog_id}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": dialog_id,
                    "name": "str",
                    "type": dialog_type.value,
                    "users": [
                        {
                            "user_id": 1,
                            "first_name": "str",
                            "last_name": "str",
                            "username": "str",
                            "phone": "str",
                        },
                        {
                            "user_id": 2,
                            "first_name": "str",
                            "last_name": "str",
                            "username": "str",
                            "phone": "str",
                        },
                    ],
                },
                f,
            )
        reader = JSONDialogReaderWriter(tmp_path)
        # Act
        result = reader.read_dialog(dialog_id)
        # Assert
        assert result == dialog

    @pytest.mark.parametrize("dialog_type", list(DialogType))
    def test_no_users(self, tmp_path, dialog_type):
        # Arrange
        dialog_id = 1
        dialog = DialogMetadata(id=dialog_id, name="str", type=dialog_type, users=[])
        with open(tmp_path / f"{dialog_id}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": dialog_id,
                    "name": "str",
                    "type": dialog_type.value,
                    "users": [],
                },
                f,
            )
        reader = JSONDialogReaderWriter(tmp_path)
        # Act
        result = reader.read_dialog(dialog_id)
        # Assert
        assert result == dialog

    def test_read_nonexistent_dialog(self, tmp_path):
        # Arrange
        dialog_id = 999
        reader = JSONDialogReaderWriter(tmp_path)
        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            reader.read_dialog(dialog_id)
        assert str(exc_info.value) == f"dialog {dialog_id} not found"

    @pytest.mark.parametrize("invalid_type", ["invalid_type", "", "123", None])
    def test_read_dialog_invalid_type(self, tmp_path, invalid_type):
        # Arrange
        dialog_id = 1
        with open(tmp_path / f"{dialog_id}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": dialog_id,
                    "name": "str",
                    "type": invalid_type,
                    "users": [],
                },
                f,
            )
        reader = JSONDialogReaderWriter(tmp_path)
        # Act & Assert
        with pytest.raises(ValueError):
            reader.read_dialog(dialog_id)


class TestReadAllDialogs:
    def test_read_all_dialogs_empty(self, tmp_path):
        # Arrange
        reader = JSONDialogReaderWriter(tmp_path)
        # Act
        result = reader.read_all_dialogs()
        # Assert
        assert result == []

    def test_read_all_dialogs_multiple_valid_dialogs(self, tmp_path):
        # Arrange
        dialogs = [
            DialogMetadata(id=1, name="Dialog1", type=DialogType.PRIVATE, users=[]),
            DialogMetadata(
                id=2,
                name="Dialog2",
                type=DialogType.GROUP,
                users=[
                    DialogMemberData(
                        user_id=10,
                        first_name="User",
                        last_name="One",
                        username="userone",
                        phone=None,
                    )
                ],
            ),
            DialogMetadata(id=3, name="Dialog3", type=DialogType.CHANNEL, users=[]),
        ]
        for dialog in dialogs:
            with open(tmp_path / f"{dialog['id']}.json", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "id": dialog["id"],
                        "name": dialog["name"],
                        "type": dialog["type"].value,
                        "users": [
                            {
                                "user_id": user["user_id"],
                                "first_name": user["first_name"],
                                "last_name": user["last_name"],
                                "username": user["username"],
                                "phone": user["phone"],
                            }
                            for user in dialog["users"]
                        ],
                    },
                    f,
                )
        reader = JSONDialogReaderWriter(tmp_path)
        # Act
        result = reader.read_all_dialogs()
        # Assert
        assert result == dialogs

    def test_read_all_dialogs_with_invalid_dialog(self, tmp_path):
        # Arrange
        valid_dialog = DialogMetadata(
            id=1, name="Dialog1", type=DialogType.PRIVATE, users=[]
        )
        invalid_dialog_id = 2
        with open(tmp_path / f"{valid_dialog['id']}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": valid_dialog["id"],
                    "name": valid_dialog["name"],
                    "type": valid_dialog["type"].value,
                    "users": [],
                },
                f,
            )
        with open(tmp_path / f"{invalid_dialog_id}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "id": invalid_dialog_id,
                    "name": "Invalid Dialog",
                    "type": "invalid_type",
                    "users": [],
                },
                f,
            )
        reader = JSONDialogReaderWriter(tmp_path)
        # Act & Assert
        with pytest.raises(ValueError):
            reader.read_all_dialogs()
