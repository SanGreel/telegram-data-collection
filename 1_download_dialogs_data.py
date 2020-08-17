import os
import argparse
import pandas as pd
import logging

import telethon

from utils.utils import init_config, read_dialogs


def init_args():
    """
    Initialize arguments

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Step #2.Download dialogs")

    parser.add_argument(
        "--dialogs_ids",
        nargs="+",
        type=str,
        help="id(s) of dialog(s) to download, -1 for all",
        required=True,
    )
    parser.add_argument(
        "--dialog_msg_limit",
        type=int,
        help="amount of messages to download from a dialog",
        default=100,
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default="config/config.json",
    )
    parser.add_argument("--debug_mode", type=int, help="Debug mode", default=0)
    parser.add_argument("--session_name", type=str, help="session name", default="tmp")

    return parser.parse_args()


def dialogs_id_input_handler(input_id_lst, dialog_list="data/dialogs"):
    """
    Functions handles input_id_lst depending on the input

    :param input_id_lst: list of all dialogs from command prompt
    :param dialog_list: list of all dialogs in meta directory
    :return:
    """
    if input_id_lst[0] == "-1":
        return [dialog_id["id"] for dialog_id in dialog_list]
    elif len(input_id_lst) == 1:
        return [int(dialog_id) for dialog_id in input_id_lst[0].split(",")]
    elif len(input_id_lst) > 1:
        return [int(dialog_id.replace(",", "")) for dialog_id in input_id_lst]


def msg_limit_input_handler(msg_limit):
    """
    Functions handles msg_limit depending on the input

    :param msg_limit: maximum amount of messages to be
                      downloaded for each dialog
    :return: msg_limit
    """
    msg_limit = 100000000 if msg_limit == -1 else msg_limit
    return msg_limit


async def download_dialog(client, id, MSG_LIMIT):
    """
    Download messages and their metadata for a specific message id,
    and save them in *ID*.csv

    :return: None
    """
    try:
        tg_entity = await client.get_entity(id)
        # path = await client.download_media(id)
        # print(path)
        messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)
    except ValueError:
        errmsg = f"No such ID found: #{id}"
        raise ValueError(errmsg,)

    dialog = []

    for m in messages:
        if m.media:
            #path = await m.download_media(file="data/media/")
            print(type(m.media))
        if hasattr(m.to_id, "user_id"):
            to_id = m.to_id.user_id
        else:
            to_id = m.to_id

        dialog.append(
            {
                "id": m.id,
                "date": m.date,
                "from_id": m.from_id,
                "to_id": to_id,
                "fwd_from": m.fwd_from,
                "message": m.message,
            }
        )

    dialog_file_path = os.path.join(config["dialogs_data_folder"], f"{str(id)}.csv")

    df = pd.DataFrame(dialog)
    df.to_csv(dialog_file_path)


if __name__ == "__main__":

    args = init_args()

    CONFIG_PATH = args.config_path
    MSG_LIMIT = msg_limit_input_handler(args.dialog_msg_limit)
    SESSION_NAME = args.session_name
    DEBUG_MODE = args.debug_mode

    config = init_config(CONFIG_PATH)
    dialogs_list = read_dialogs(config["dialogs_list_folder"])
    client = telethon.TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

    DIALOGS_ID = dialogs_id_input_handler(args.dialogs_ids, dialogs_list)

    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)

    if not os.path.exists(config["dialogs_data_folder"]):
        os.mkdir(config["dialogs_data_folder"])

    for id in DIALOGS_ID:
        print(f"Loading dialog #{id}")

        with client:
            client.loop.run_until_complete(download_dialog(client, id, MSG_LIMIT))
