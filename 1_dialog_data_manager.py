import json
import os

if __name__ == "__main__":

    metadata_folder = 'data/meta/'
    files = os.listdir(metadata_folder)

    n = 1

    for f in files:
        dialog_path = os.path.join(metadata_folder, f)

        with open(dialog_path, 'r') as read_file:
            dialogs_data = json.load(read_file)
            dialogs_list = []
            dialogs_list.append(dialogs_data)

            for dialog in dialogs_list:
                print(f'\ndialog #{n}')
                n += 1

                for element in dialog.items():
                    key, val = element
                    print("{:<20} {:<15}".format(key, val))





# # Entity = объект, in this case, it's a dialog id and we pass it to the 'get_massages' method
# text = ''
# channel_entity = await client.get_entity(dialog_id)
# messages = await client.get_messages(channel_entity, ids=325314319)
#
# print(messages)
#
# for m in messages:
#     text = text + '\n' + str(messages)
#
#     with open(msg_folder+str(id)+".txt", "w") as text_file:
#         text_file.write(messages)
