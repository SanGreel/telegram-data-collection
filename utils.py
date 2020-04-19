import json

from telethon import TelegramClient, events, sync, errors


def init_config(config_path):
    with open(config_path) as json_file:
        config = json.load(json_file)
        return config
    return None


def init_client(session_name, api_id, api_hash):
    return TelegramClient(session_name, api_id, api_hash)