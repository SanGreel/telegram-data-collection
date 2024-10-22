import json
import logging
from pathlib import Path

from ..dict_types.dialog import DialogMetadata, DialogType


logger = logging.getLogger(__name__)


class JSONDialogWriter:
    def __init__(self, list_dir: Path) -> None:
        self.list_dir = list_dir
        self.list_dir.mkdir(parents=True, exist_ok=True)

    def read_dialogs(self) -> list[DialogMetadata]:
        dialogs = []
        for dialog_path in self.list_dir.glob("*.json"):
            with open(dialog_path, "r", encoding="utf-8") as f:
                dialog: dict = json.load(f)
                # post format data
                dialog["type"] = DialogType(dialog["type"])
                dialogs.append(dialog)
        logger.info(f"loaded {len(dialogs)} dialogs")
        return dialogs

    def write_dialog(self, data: DialogMetadata) -> None:
        # preformat data
        output = dict(data)
        output["type"] = data["type"].value

        write_path = self.list_dir / f"{data['id']}.json"
        with open(write_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        logger.info(f"saved #{data['id']} to {write_path}")
