import os
import json
from glob import glob

from telethon import TelegramClient, events, sync, errors


def init_config(config_path):
    with open(config_path) as json_file:
        config = json.load(json_file)
        return config
    return None


def init_tg_client(session_name, api_id, api_hash):
    return TelegramClient(session_name, api_id, api_hash)


def read_dialogs(metadata_folder='data/meta/', metadata_format='json'):
    if os.path.isdir(metadata_folder):
        dialogs_list = []

        files = glob(f'{metadata_folder}/*.{metadata_format}')

        for dialog_path in files:
            with open(dialog_path, 'r') as read_file:
                dialogs_data = json.load(read_file)
                dialogs_list.append(dialogs_data)

        return dialogs_list
    return None
