from telethon import TelegramClient, events, sync

api_id = 1310963
api_hash = 'c3647146b1aeb55cae072386b07b08dc'

client = TelegramClient('julia', api_id, api_hash)


async def main():
    async for dialog in client.iter_dialogs():
        print('{:>14}: {}'.format(dialog.id, dialog.title))

    # message = await client.get_messages(ids)
    # print(message)

with client:
    client.loop.run_until_complete(main())
