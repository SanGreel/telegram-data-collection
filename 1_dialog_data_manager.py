import json
import os

if __name__ == "__main__":

    meta_folder = 'data/meta/'
    files = os.listdir(meta_folder)

    for f in files:
        path = meta_folder + f
        print(path)

        with open(f, 'r', encoding="ISO-8859-1") as read_file:
            dialogs_list = json.load(read_file)
            for i in dialogs_list['id']['name']:
                print(i)


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






