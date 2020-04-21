import json
import argparse
import os

from utils import init_config, init_client

session_name = 'tmp'


def save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog):
    # TODO: 2. fix encoding problem
    metadata = {
        "id": dialog_id,
        "name": name_of_dialog,
        "users": users_names,
        "type": type_of_dialog
    }

    print(metadata)

    dialog_file_path = config['meta_folder'] + str(dialog_id) + ".json"
    with open(dialog_file_path, "w+", encoding='utf8') as meta_file:
        json.dump(metadata, meta_file)
        print(f"saved {dialog_file_path}")
        print('\n')


if __name__ == "__main__":
    meta_path = r'data/meta'

    if not os.path.exists(meta_path):
        os.mkdir(meta_path)

    parser = argparse.ArgumentParser(description='Download dialogs meta data for account.')

    parser.add_argument('--dialogs_limit', type=int, help='number of dialogs')
    parser.add_argument('--config_path', type=str, help='path to config file', default='config/config.json')
    parser.add_argument('--debug_mode', type=int, help='Debug mode', default=0)
    parser.add_argument('--dialog_id', type=int, help='id of dialog to download')

    args = parser.parse_args()
    print(args)

    CONFIG_PATH = args.config_path
    DEBUG_MODE = args.debug_mode
    DIALOGS_LIMIT = args.dialogs_limit
    DIALOG_ID = args.dialog_id

    j_and_a_dialog_id = 331192040

    config = init_config(CONFIG_PATH)
    client = init_client(session_name, config['api_id'], config['api_hash'])


    # TODO: fix problem with msg, and meta_folder. They aren't variables now, they are in the config var

    async def main():
        dialogs = await client.get_dialogs()

        k = 1

        # Getting id for each dialog in the list of dialogs
        for d in dialogs:
            # print(DIALOGS_LIMIT)
            if DIALOGS_LIMIT != -1 and k > DIALOGS_LIMIT:
                exit(0)
            print(f'step #{k}')

            k += 1

            dialog_id = d.id
            name_of_dialog = d.name
            users_names = []

            if d.is_user == True:
                type_of_dialog = "Private dialog"
            elif d.is_group == True:
                type_of_dialog = "Group type"
            elif d.is_channel == True:
                type_of_dialog = "Channel type"

            # TODO: 3. fix downloading of users list, only exception branch works now
            try:
                async for u in client.get_participants(d):
                    save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)

            # TODO: 4. add proper exception (Andrew)
            except:

                print('we are here')
                save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)

                print(f'ChatAdminRequiredError for {name_of_dialog}')
                print('\n\n')


    with client:
        client.loop.run_until_complete(main())
