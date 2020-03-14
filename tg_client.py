from telethon import TelegramClient, events, sync

api_id = 1310963
api_hash = 'c3647146b1aeb55cae072386b07b08dc'

client = TelegramClient('session name', api_id, api_hash)
client.start()