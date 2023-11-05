import glob
import os
import argparse
from typing import Dict

import pandas as pd
import logging
import json

import telethon

from utils.utils import init_config, read_dialogs


dialog_file_path = os.path.join("../data/test.csv")

dialog = []
dialog.append(
    {
        "id": 1,
        "message": """як можу в "С++,",","," просто розпарсити список списків
типу такого: [[4,2,1],[5,7,0],[5,0,3],[2,4],[0,3],[1,2,6],[5,7],[1,6]]

от у хаскелі просто read і готово все""",
    }
)
dialog.append(
    {
        "id": 2,
        "message": "До речі, вони до сих пір там набирають мабуть",
    }
)
dialog.append(
    {
        "id": 3,
        "message": "test, test, test \n test, test",
    }
)

df = pd.DataFrame(dialog)
df.to_csv(dialog_file_path, encoding="utf-8")

# d = glob.glob("../data/test/*.csv")
local_df = pd.read_csv("../data/test.csv", encoding="utf-8")
print(local_df)
