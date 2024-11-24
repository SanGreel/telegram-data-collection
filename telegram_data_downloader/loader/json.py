import json
import logging
from pathlib import Path

from ..dict_types.dialog import DialogMetadata, DialogType


logger = logging.getLogger(__name__)


class JSONDialogReaderWriter:
    """
    Class for reading and writing dialog metadata to JSON files.
    """

    def __init__(self, list_dir: Path) -> None:
        self.list_dir = list_dir
        self.list_dir.mkdir(parents=True, exist_ok=True)

    def read_dialog(self, dialog_id: int) -> DialogMetadata:
        """
        Read dialog metadata by `dialog_id` from a JSON file.
        """
        dialog_path = self.list_dir / f"{dialog_id}.json"
        if not dialog_path.exists():
            raise FileNotFoundError(f"dialog {dialog_id} not found")
        with open(dialog_path, "r", encoding="utf-8") as f:
            dialog: dict = json.load(f)
            # post format data
            dialog["type"] = DialogType(dialog["type"])
        logger.debug("loaded #%d from %s", dialog_id, dialog_path)
        return DialogMetadata(**dialog)

    def read_all_dialogs(self) -> list[DialogMetadata]:
        """
        Using the `list_dir` attribute, read all dialog metadata from JSON files.
        """
        dialog_ids = [int(path.stem) for path in self.list_dir.glob("*.json")]
        dialogs = [self.read_dialog(dialog_id) for dialog_id in dialog_ids]
        logger.debug("loaded %d dialogs", len(dialogs))
        return dialogs

    def write_dialog(self, data: DialogMetadata) -> None:
        """
        Write dialog metadata to a JSON file.
        """
        # preformat data
        output = dict(data)
        output["type"] = data["type"].value

        write_path = self.list_dir / f"{data['id']}.json"
        with open(write_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        logger.debug("saved #%d to %s", data["id"], write_path)
