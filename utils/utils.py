import os
import json
from glob import glob


def init_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("Config file doesn't exist\n"
                        f"Please, create a new config file here {config_path}")
        # api_id, api_hash = "", ""
        # config = {}
        #
        # # create config.json file
        # while not api_id.isdigit() or not api_hash:
        #     api_id = input("Input your api_id or 'q' to exit: ")
        #     if "q" == api_id:
        #         break
        #     api_hash = input("Input your api_hash or 'q' to exit: ")
        #     if "q" == api_hash:
        #         break
        #
        # config["api_id"] = api_id
        # config["api_hash"] = api_hash

    else:
        with open(config_path) as json_file:
            config = json.load(json_file)

    default_data_folder = "../data"
    if config["dialogs_data_folder"].startswith(default_data_folder) and not os.path.exists(default_data_folder):
        os.mkdir(default_data_folder)

    if not os.path.exists(config["dialogs_data_folder"]):
        os.mkdir(config["dialogs_data_folder"])

    if not os.path.exists(config["dialogs_list_folder"]):
        os.mkdir(config["dialogs_list_folder"])

    with open(config_path, "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4, ensure_ascii=True)

    return config


def read_dialogs(metadata_folder, metadata_format="json"):
    if os.path.isdir(metadata_folder):
        dialogs_list = []

        files = glob(f"{metadata_folder}/*.{metadata_format}")

        for dialog_path in files:
            with open(dialog_path, "r", encoding="utf-8") as read_file:
                dialogs_data = json.load(read_file)
                dialogs_list.append(dialogs_data)

        return dialogs_list
    return None


def save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog, dialogs_list_folder="data/dialogs_list"):
    metadata = {
        "id": dialog_id,
        "name": name_of_dialog,
        "type": type_of_dialog,
        "users": users_names
    }

    dialog_file_path = os.path.join(dialogs_list_folder, str(dialog_id) + ".json")

    with open(dialog_file_path, "w", encoding="utf8") as meta_file:
        json.dump(metadata, meta_file, indent=4, ensure_ascii=False)
        print(f"saved {dialog_file_path}")
        print("\n")
