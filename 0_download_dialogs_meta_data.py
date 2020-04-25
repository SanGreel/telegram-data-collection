import json
import argparse
import os

from utils import init_config, init_tg_client

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

    dialog_file_path = config['dialogs_metadata_folder'] + str(dialog_id) + ".json"
    with open(dialog_file_path, "w+", encoding='utf8') as meta_file:
        json.dump(metadata, meta_file)
        print(f"saved {dialog_file_path}")
        print('\n')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Download dialogs meta data for account.')

    parser.add_argument('--dialogs_limit', type=int, help='number of dialogs', required=True)
    parser.add_argument('--config_path', type=str, help='path to config file', default='config/config.json')
    parser.add_argument('--debug_mode', type=int, help='Debug mode', default=0)

    args = parser.parse_args()
    print(args)

    CONFIG_PATH = args.config_path
    DEBUG_MODE = args.debug_mode
    DIALOGS_LIMIT = args.dialogs_limit

    j_and_a_dialog_id = 331192040

    config = init_config(CONFIG_PATH)
    client = init_tg_client(session_name, config['api_id'], config['api_hash'])

    if not os.path.exists(config['dialogs_metadata_folder']):
        os.mkdir(config['dialogs_metadata_folder'])

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



    # # both arguments are empty
    # if SHOW_DIALOGS is None \
    #         and DIALOG_ID is None:
    #     # print('ERROR: at least one argument should be passed')
    #     raise ValueError('ERROR: at least one argument should be passed')
    #
    # if not os.path.exists(config['msg_folder']):
    #     os.mkdir(config['msg_folder'])
    #
    # # TODO: check if can be improved
    # if MSG_LIMIT == -1:
    #     MSG_LIMIT = 1000000000
    #
    #
    #
    # # show dialogs list
    # if SHOW_DIALOGS is not None:
    #     number_of_dialogs_to_show = SHOW_DIALOGS
    #
    #     if number_of_dialogs_to_show > len(dialogs_list):
    #         number_of_dialogs_to_show = len(dialogs_list)
    #
    #     show_dialogs(number_of_dialogs_to_show)
    #
    # # download single dialog          -1001314742214
    #                                          -1001314742214

    # parser.add_argument('--show_dialogs', type=int, help='number of dialogs to show', default=None)
    # def show_dialogs(n):
    #     for i in range(0, number_of_dialogs_to_show):
    #         dialog = dialogs_list[i]
    #         print(f"ID #{dialog['id']}")
    #         print(f"{dialog['name']}")
    #         print('\n')
    with client:
        client.loop.run_until_complete(main())
