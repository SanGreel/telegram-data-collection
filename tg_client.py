from telethon import TelegramClient, events, sync



if __name__ == "__main__":
    api_id =
    api_hash = ''

    msg_folder = 'data/msg/'

    j_and_a_dialog_id = 325314319
    msg_limit = 10

    session_name = 'tmp2'

    client = TelegramClient(session_name, api_id, api_hash)

    async def main():
        dialogs = await client.get_dialogs()

        for d in dialogs:
            id = d.id

            text = ''

            channel_entity = await client.get_entity(id)
            messages = await client.get_messages(channel_entity, limit=msg_limit)

            for m in messages:
                text = text + '\n' + str(m.message)

            print(id)

            with open(msg_folder+str(id)+".txt", "w") as text_file:
                text_file.write(text)

    with client:
        client.loop.run_until_complete(main())
