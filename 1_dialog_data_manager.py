import json
import os
import argparse
import csv
import pandas as pd

from utils import init_config, init_client

session_name = 'tmp'


def read_dialogs(metadata_folder = 'data/meta/'):
    dialogs_list = []
    files = os.listdir(metadata_folder)

    for f in files:
        dialog_path = os.path.join(metadata_folder, f)

        with open(dialog_path, 'r') as read_file:
            dialogs_data = json.load(read_file)
            dialogs_list.append(dialogs_data)
    return dialogs_list


def show_dialogs(n):
    for i in range(0, number_of_dialogs_to_show):
        dialog = dialogs_list[i]
        print(f"ID #{dialog['id']}")
        print(f"{dialog['name']}")
        print('\n')


if __name__ == "__main__":
    metadata_folder = 'data/meta/'
    dialogs_list = read_dialogs(metadata_folder)

    parser = argparse.ArgumentParser(description='Download dialogs meta data for account.')

    parser.add_argument('--show_dialogs', type=int, help='number of dialogs to show', default=None)
    parser.add_argument('--dialog_id', type=int, help='id of dialog to download')
    parser.add_argument('--dialog_msg_limit', type=int, help='amount of messages to download from one dialog', default=100)
    parser.add_argument('--config_path', type=str, help='path to config file', default='config/config.json')

    args = parser.parse_args()
    # print(args)

    CONFIG_PATH = args.config_path
    SHOW_DIALOGS = args.show_dialogs
    DIALOG_ID = args.dialog_id
    MSG_LIMIT = args.dialog_msg_limit

    # TODO: check if can be improved
    if MSG_LIMIT == -1:
        MSG_LIMIT = 1000000000

    # both arguments are empty
    if SHOW_DIALOGS is None \
            and DIALOG_ID is None:
        print('ERROR: at least one argument should be passed')

    # show dialogs list
    if SHOW_DIALOGS is not None:
        number_of_dialogs_to_show = SHOW_DIALOGS

        if number_of_dialogs_to_show > len(dialogs_list):
            number_of_dialogs_to_show = len(dialogs_list)

        show_dialogs(number_of_dialogs_to_show)

    # download single dialog
    if DIALOG_ID is not None:
        config = init_config(CONFIG_PATH)
        client = init_client(session_name, config['api_id'], config['api_hash'])

        async def not_main():
            channel_entity = await client.get_entity(DIALOG_ID)
            messages = await client.get_messages(channel_entity, limit=MSG_LIMIT)

            dialog = []

            for m in messages:
                dialog.append({
                    "id": m.id,
                    "date": m.date,
                    "from_id": m.from_id,
                    "to_id": m.to_id.user_id,
                    "fwd_from": m.fwd_from,
                    "message": m.message
                })

                print(f'dwnld {m.id}')

            dialog_file_path = config['msg_folder'] + '/' + str(DIALOG_ID) + ".csv"

            df = pd.DataFrame(dialog)
            df.to_csv(dialog_file_path)

        with client:
            client.loop.run_until_complete(not_main())
