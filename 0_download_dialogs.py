
import json
import argparse


from telethon import TelegramClient, events, sync, errors

session_name = 'tmp'


def save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog):
    # TODO: fix encoding problem
    metadata = {
        "id": dialog_id,
        "name": name_of_dialog,
        "users": users_names,
        "type": type_of_dialog
    }

    print(metadata)

    dialog_file_path = meta_folder + str(dialog_id) + ".json"
    with open(dialog_file_path, "w+", encoding='utf8') as meta_file:
        json.dump(metadata, meta_file)
        print(f'saved {dialog_file_path}')
        print('\n')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Download dialogs data for account.')

    parser.add_argument('--dialogs_limit', type=int, help='number of diaglos', required=True)
    parser.add_argument('--config_path', type=str, help='path to config file', default='config/config.json')
    parser.add_argument('--debug_mode', type=int, help='Debug mode', default=0)

    args = parser.parse_args()
    print(args)

    CONFIG_PATH = args.config_path
    DEBUG_MODE = args.debug_mode
    DIALOGS_LIMIT = args.dialogs_limit

    with open(CONFIG_PATH) as json_file:
        config = json.load(json_file)

    api_id = config['api_id']
    api_hash = config['api_hash']

    msg_folder = 'data/msg/'
    meta_folder = 'data/meta/'

    j_and_a_dialog_id = 325314319


    client = TelegramClient(session_name, api_id, api_hash)

    async def main():
        dialogs = await client.get_dialogs()

        k = 0

        # Getting id for each dialog in the list of dialogs
        for d in dialogs:
            print(f'step #{k}')
            # print(DIALOGS_LIMIT)
            if DIALOGS_LIMIT != -1 and k > DIALOGS_LIMIT:
                print('exit')
                exit(0)

            k += 1

            dialog_id = d.id
            name_of_dialog = d.name


            if d.is_user == True:
                type_of_dialog = "Private dialog"
            elif d.is_group == True:
                type_of_dialog = "Group type"
            elif d.is_channel == True:
                type_of_dialog = "Channel type"

            try:
                async for user in client.iter_participants(d):
                    users_names = user.username
                    save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)
            # TODO: add proper exception (Andrew)
            except:
                users_names = 'AdminRequiredError'
                save_dialog(dialog_id, name_of_dialog, users_names, type_of_dialog)

                print(f'ChatAdminRequiredError for {name_of_dialog}')
                print('\n\n')


    with client:
        client.loop.run_until_complete(main())
