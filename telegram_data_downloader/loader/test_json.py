import json

import pytest

from ..dict_types.dialog import DialogMetadata, DialogType, DialogMemberData
from .json import JSONDialogReaderWriter


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
        with open(tmp_path / f"{dialog_id}.json") as f:
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
        with open(tmp_path / f"{dialog_id}.json") as f:
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
        with open(tmp_path / f"{dialog_id}.json", "w") as f:
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
        with open(tmp_path / f"{dialog_id}.json", "w") as f:
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
