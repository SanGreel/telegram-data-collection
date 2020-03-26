#TODO: create a README file with project description, diagram and how to run
#TODO: two methods: 1.to show list of all dialogs (read from jsons) 2.download dialog by ID

# Entity = объект, in this case, it's a dialog id and we pass it to the 'get_massages' method
text = ''
channel_entity = await client.get_entity(dialog_id)
messages = await client.get_messages(channel_entity, ids=325314319)

print(messages)

for m in messages:
    text = text + '\n' + str(messages)

    with open(msg_folder+str(id)+".txt", "w") as text_file:
        text_file.write(messages)