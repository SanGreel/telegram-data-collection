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

        except TypeError:
            print("ERROR!!!!! with getting participants of the dialog")
            save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)

        except telethon.errors.rpcerrorlist.ChatAdminRequiredError as error:
            print("ERROR!!!!! ", error)
            save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)


def make_config_client_access(config_path, session_name):
    if not os.path.exists(config_path):
        api_id, api_hash = "", ""

        # create config.json file
        while not api_id.isdigit() or not api_hash:
            api_id = input("Input your api_id or 'q' to exit: ")
            if "q" == api_id:
                break
            api_hash = input("Input your api_hash or 'q' to exit: ")
            if "q" == api_hash:
                break

        with open(os.path.join("config", "config_example.json"), "r", encoding="utf-8") as json_file:
            config = json.load(json_file)

        config["api_id"] = api_id
        config["api_hash"] = api_hash

    else:
        config = init_config(config_path)

    client = TelegramClient(session_name, config["api_id"], config["api_hash"])

    if not os.path.exists(config["dialogs_metadata_folder"]):
        os.mkdir(config["dialogs_metadata_folder"])

    with open(config_path, "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4, ensure_ascii=True)

    return client


if __name__ == "__save_user_dialogs__":
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

    # start saving dialogs of the special user
    client = make_config_client_access(CONFIG_PATH, SESSION_NAME)
    with client:
        client.loop.run_until_complete(save_user_dialogs(client, DIALOGS_LIMIT))
