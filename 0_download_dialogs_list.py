import argparse
import os

import telethon
from telethon import TelegramClient

from utils.utils import init_config, save_dialog


def init_args():
    """
    Initialize arguments

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Download dialogs list for user."
    )

    parser.add_argument(
        "--dialogs_limit", type=int, help="number of dialogs", required=True
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default=os.path.join("config", "config.json"),
    )
    parser.add_argument("--debug_mode", type=int, help="Debug mode", default=0)
    parser.add_argument("--session_name", type=str, help="session name", default="tmp")

    # read arguments from terminal
    return parser.parse_args()


async def save_dialogs(client, dialogs_limit):
    dialogs = await client.get_dialogs()

    # Getting id for each dialog in the list of dialogs
    for n_dialog, dialog in enumerate(dialogs):
        print(vars(dialog))
        if dialogs_limit == n_dialog:
            exit(0)

        dialog_id = dialog.id
        dialog_name = dialog.name
        dialog_members = []

        print(f"dialog #{dialog_id}")

        dialog_type = ""
        if dialog.is_user:
            dialog_type = "Private dialog"
        elif dialog.is_group:
            dialog_type = "Group"
        elif dialog.is_channel:
            dialog_type = "Channel"

        try:
            users = await client.get_participants(dialog)

            for user in users:
                if user.username is not None:
                    user_data = {
                        "user_id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "phone": user.phone,
                    }
                    dialog_members.append(user_data)

        except telethon.errors.rpcerrorlist.ChatAdminRequiredError as error:
            print("ERROR\n", error)

        save_dialog(dialog_id, dialog_name, dialog_members, dialog_type, DIALOGS_LIST_FOLDER)


if __name__ == "__main__":
    args = init_args()

    CONFIG_PATH = args.config_path
    DEBUG_MODE = args.debug_mode
    DIALOGS_LIMIT = args.dialogs_limit
    SESSION_NAME = args.session_name

    config = init_config(CONFIG_PATH)
    client = TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

    DIALOGS_LIST_FOLDER = config["dialogs_list_folder"]

    # save dialogs
    with client:
        client.loop.run_until_complete(save_dialogs(client, DIALOGS_LIMIT))
