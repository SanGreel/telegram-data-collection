import csv
from typing import Any
from datetime import datetime

from telegram_data_downloader.loader.csv import CSVMessageWriter
from telegram_data_downloader.dict_types.message import MessageType, PeerID, MessageAttributes
from telegram_data_downloader.dict_types.dialog import DialogMetadata, DialogType


def assert_message_json_equal(msg1: dict[str, Any], msg2: dict[str, Any]):
    assert msg1.keys() == msg2.keys()
    for key in msg1:
        if key == "date":
            assert datetime.fromisoformat(msg1[key]) == datetime.fromisoformat(
                msg2[key]
            )
        elif key == "reactions":
            assert eval(msg1[key]) == eval(msg2[key])  # pylint: disable=eval-used
        else:
            assert msg1[key] == msg2[key]


def test_write_message(tmp_path):
    # Arrange
    now = datetime.now()
    msg = MessageAttributes(
        id=1,
        date=now,
        from_id=PeerID(1),
        fwd_from=None,
        message="str",
        type=MessageType.PHOTO,
        duration=1,
        to_id=PeerID(2),
        reactions={PeerID(1): "smth"},
    )
    dialog = DialogMetadata(id=1, name="test_dialog", type=DialogType.PRIVATE, users=[])
    writer = CSVMessageWriter(tmp_path)
    # Act
    writer.write_messages(dialog, [msg])
    # Assert
    with open(tmp_path / f"{dialog['id']}.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = next(reader)
    assert_message_json_equal(
        data,
        {
            "id": "1",
            "date": now.isoformat(sep=" "),
            "from_id": "1",
            "fwd_from": "",
            "message": "str",
            "type": "photo",
            "duration": "1",
            "to_id": "2",
            "reactions": str(msg["reactions"]),
        },
    )


def test_message_list_empty(tmp_path):
    # Arrange
    dialog = DialogMetadata(id=1, name="test_dialog", type=DialogType.PRIVATE, users=[])
    writer = CSVMessageWriter(tmp_path)
    # Act
    writer.write_messages(dialog, [])
    # Assert
    with open(tmp_path / f"{dialog['id']}.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert not list(reader)
