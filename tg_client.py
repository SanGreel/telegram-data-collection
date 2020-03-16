import configparser
import json


from telethon import TelegramClient, events, sync

# api_id = 1310963
# api_hash = 'c3647146b1aeb55cae072386b07b08dc'
session_name = 'tmp'


if __name__ == "__main__":

    with open('config.json') as json_file:
        config = json.load(json_file)

    api_id = config['api_id']
    api_hash = config['api_hash']   

    msg_folder = 'data/msg/'

    j_and_a_dialog_id = 325314319
    msg_limit = 10

    client = TelegramClient(session_name, api_id, api_hash)

    async def main():
        dialogs = await client.get_dialogs()
        
        # Getting id for each dialog in the list of dialogs  
        for d in dialogs:
            id = d.id

            text = ''

        # Entity = объект, in this case, it's a dialog id and we pass it to the 'get_massages' method
            channel_entity = await client.get_entity(id)
            messages = await client.get_messages(channel_entity, limit=msg_limit)

            for m in messages:
                text = text + '\n' + str(m.message)

            print(id)

            with open(msg_folder+str(id)+".txt", "w") as text_file:
                text_file.write(text)

    with client:
        client.loop.run_until_complete(main())
