import logging
from pathlib import Path

import pandas as pd

from ..dict_types.dialog import DialogMetadata
from ..dict_types.message import MessageAttributes


logger = logging.getLogger(__name__)


class CSVMessageWriter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_messages(
        self, dialog: DialogMetadata, messages: list[MessageAttributes]
    ) -> None:
        df = pd.DataFrame(messages)
        write_path = self.output_dir / f"{dialog['id']}.csv"
        df.to_csv(write_path, index=False)
        logger.info(f"saved messages for {dialog['id']} to {write_path}")
