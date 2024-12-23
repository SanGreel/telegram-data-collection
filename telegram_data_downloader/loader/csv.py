import logging
from pathlib import Path
from typing import get_type_hints

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
        """
        Write messages for a dialog to a CSV file.
        """
        if messages:
            df = pd.DataFrame(messages)
        else:
            columns = list(get_type_hints(MessageAttributes).keys())
            df = pd.DataFrame(columns=columns)
        df["type"] = df["type"].apply(lambda x: x.value)
        write_path = self.output_dir / f"{dialog['id']}.csv"
        df.to_csv(write_path, index=False)
        logger.debug("saved messages for %d to %s", dialog["id"], write_path)
