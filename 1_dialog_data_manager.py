import json
import os
import argparse


def read_dialogs(metadata_folder = 'data/meta/'):
    dialogs_list = []
    files = os.listdir(metadata_folder)

    for f in files:
        dialog_path = os.path.join(metadata_folder, f)

        with open(dialog_path, 'r') as read_file:
            dialogs_data = json.load(read_file)
            dialogs_list.append(dialogs_data)
    return dialogs_list



if __name__ == "__main__":
    metadata_folder = 'data/meta/'
    dialogs_list = read_dialogs(metadata_folder)

    parser = argparse.ArgumentParser(description='Download dialogs meta data for account.')

    parser.add_argument('--show_dialogs', type=int, help='number of dialogs to show', required=True)
    parser.add_argument('--dialog_id', type=int, help='id of dialog to download')

    args = parser.parse_args()
    print(args)

    SHOW_DIALOGS = args.show_dialogs
    DIALOG_ID = args.dialog_id

    n = 1

    for dialog in dialogs_list:
        print(f'\ndialog #{n}')
        # print(SHOW_DIALOGS)
        if SHOW_DIALOGS != -1 and n > SHOW_DIALOGS:
            print('exit')
            exit(0)

        n += 1

        for element in dialog.items():
            key, val = element
            print("{:<20} {:<15}".format(key, val))

    # channel_entity = await client.get_entity(DIALOG_ID)
    # messages = await client.get_messages(channel_entity, ids=DIALOG_ID)
    #
    # print(messages)





# # Entity = объект, in this case, it's a dialog id and we pass it to the 'get_massages' method
# text = ''

#
# for m in messages:
#     text = text + '\n' + str(messages)
#
#     with open(msg_folder+str(id)+".txt", "w") as text_file:
#         text_file.write(messages)
