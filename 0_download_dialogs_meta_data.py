import argparse
import json
import os

import telethon
from telethon import TelegramClient

from utils.utils import init_config, save_dialog


async def save_user_dialogs(client, dialogs_limit):
    dialogs = await client.get_dialogs()

    # Getting id for each dialog in the list of dialogs
    for n_dialog, dialog in enumerate(dialogs):
        if dialogs_limit == n_dialog:
            exit(0)
        print(f"step #{n_dialog + 1}")

        dialog_id = dialog.id
        name_of_dialog = dialog.name
        users_names = []

        type_of_dialog = ""
        if dialog.is_user:
            type_of_dialog = "Private dialog"
        elif dialog.is_group:
            type_of_dialog = "Group"
        elif dialog.is_channel:
            type_of_dialog = "Channel"

        try:
            users = await client.get_participants(dialog)

            for user in users:
                if user.username is not None:
                    user_dict = {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "phone": user.phone,
                    }
                    users_names.append(user_dict)

            save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)

        except telethon.errors.rpcerrorlist.ChatAdminRequiredError as error:
            print("ERROR!!!!! ", error)
            save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)


def get_client_access(config_path, session_name):
    config = init_config(config_path)
    client = TelegramClient(session_name, config["api_id"], config["api_hash"])
    return client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download dialogs meta data for account."
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
    args = parser.parse_args()

    CONFIG_PATH = args.config_path
    DEBUG_MODE = args.debug_mode
    DIALOGS_LIMIT = args.dialogs_limit
    SESSION_NAME = args.session_name

    # save user dialoges
    client = get_client_access(CONFIG_PATH, SESSION_NAME)
    with client:
        client.loop.run_until_complete(save_user_dialogs(client, DIALOGS_LIMIT))
