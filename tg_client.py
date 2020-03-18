import configparser
import json


from telethon import TelegramClient, events, sync, errors

session_name = 'tmp'


if __name__ == "__main__":

    with open('config/config.json') as json_file:
        config = json.load(json_file)

    api_id = config['api_id']
    api_hash = config['api_hash']   

    msg_folder = 'data/msg/'
    meta_folder = 'data/meta/'

    j_and_a_dialog_id = 325314319
    msg_limit = 10

    client = TelegramClient(session_name, api_id, api_hash)

    async def main():
        dialogs = await client.get_dialogs()
        
        # Getting id for each dialog in the list of dialogs  
        for d in dialogs:
            dialog_id = d.id
            name_of_dialog = d.name


            if d.is_user == True:
                type_of_dialog = "Private dialog"
            elif d.is_group == True:
                type_of_dialog = "Group type"
            elif d.is_channel == True:
                type_of_dialog = "Channel type"

            print(type_of_dialog)

        #     try:
        #         async for user in client.iter_participants(d):
        #             users_names = user.username
        # # TODO: add proper exception 
        #     except:
        #         # print("ChatAdminRequiredError")
    
        #         metadata = {
        #             "id": dialog_id,
        #             "name": name_of_dialog,
        #             "users": users_names
        #     }

        #         with open(meta_folder+str(dialog_id)+".json", "w") as meta_file:
        #             json.dump(metadata, meta_file)


            # text = ''

        # Entity = объект, in this case, it's a dialog id and we pass it to the 'get_massages' method
            # channel_entity = await client.get_entity(dialog_id)
            # messages = await client.get_messages(channel_entity, limit=msg_limit)

            # for m in messages:
            #     text = text + '\n' + str(m.message)

            # with open(msg_folder+str(id)+".txt", "w") as text_file:
            #     text_file.write(text)



    

    with client:
        client.loop.run_until_complete(main())
