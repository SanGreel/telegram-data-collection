import os
import json
import re
from word2number import w2n
from glob import glob

from telethon import TelegramClient, events, sync, errors


def init_config(config_path):
    with open(config_path) as json_file:
        config = json.load(json_file)
        return config
    return None


def init_tg_client(session_name, api_id, api_hash):
    return TelegramClient(session_name, api_id, api_hash)


def read_dialogs(metadata_folder="data/dialogs_meta/", metadata_format="json"):
    if os.path.isdir(metadata_folder):
        dialogs_list = []

        files = glob(f"{metadata_folder}/*.{metadata_format}")

        for dialog_path in files:
            with open(dialog_path, "r") as read_file:
                dialogs_data = json.load(read_file)
                dialogs_list.append(dialogs_data)

        return dialogs_list
    return None


def save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog):
    # TODO: 2. fix encoding problem
    metadata = {
        "id": dialog_id,
        "name": name_of_dialog,
        "users": users_names,
        "type": type_of_dialog,
    }

    dialog_file_path = "data/dialogs_meta/" + str(dialog_id) + ".json"
    with open(dialog_file_path, "w+", encoding="utf8") as meta_file:
        json.dump(metadata, meta_file)
        print(f"saved {dialog_file_path}")
        print("\n")


def prepare_msg(msg: str):
    """
    Deletes symbols, converts words to numbers, prepares urls.
    :param msg: str
    :return: str
    """
    url_extract = re.compile(r'(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)?(?:https?:\/\/)'
                             r'(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)(?:[-a-zA-Z0'
                             r'-9@:%_\+.~#?&//=]*)?')
    symb_pattern = re.compile(r"[-!$%^&*()_+|~=`{}\[\]:';<>?,ʼ\/]|[^\w]")
    out_msg = []
    for word in str(msg).split():
        if url_extract.findall(word):
            word = url_extract.findall(word)[0]
        else:
            try:
                word = str(w2n.word_to_num(word))
            except ValueError:
                pass
            word = re.sub(symb_pattern, ' ', word)
        out_msg.append(word)
    out_msg = re.sub(r'\s\s+', ' ', ' '.join(out_msg))
    return out_msg
