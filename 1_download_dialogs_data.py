import os
import argparse
from typing import Dict

import pandas as pd
import logging
import json

import telethon

from utils.utils import init_config, read_dialogs

REACTIONS_LIMIT_PER_MESSAGE = 100


def init_args():
    """
    Initialize arguments

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Step #2.Download dialogs")

    parser.add_argument(
        "--dialogs_ids",
        nargs="+",
        type=str,
        help="id(s) of dialog(s) to download, -1 for all",
        required=True,
    )
    parser.add_argument(
        "--dialog_msg_limit",
        type=int,
        help="amount of messages to download from a dialog, -1 for all",
        default=10000,
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default="config/config.json",
    )
    parser.add_argument("--debug_mode", type=int, help="Debug mode", default=0)
    parser.add_argument("--session_name", type=str, help="session name", default="tmp")
    parser.add_argument('--skip_private', action='store_true')
    parser.add_argument('--skip_groups', action='store_true')
    parser.add_argument('--skip_channels', action='store_true')
    parser.add_argument('--continuation', action='store_true', help="Enable continuation mode to resume from last downloaded message")

    return parser.parse_args()


def dialogs_id_input_handler(input_id_lst, is_dialog_type_accepted, dialog_list="data/dialogs"):
    """
    Functions handles input_id_lst depending on the input

    :param input_id_lst: list of all dialogs from command prompt
    :param is_dialog_type_accepted:
    :param dialog_list: list of all dialogs in meta directory
    :return:
    """

    if input_id_lst[0] == "-1":
        return [dialog["id"] for dialog in dialog_list if is_dialog_type_accepted[dialog["type"]]]
    elif len(input_id_lst) == 1:
        provided_ids = [int(dialog_id) for dialog_id in input_id_lst[0].split(",")]
        return [dialog["id"] for dialog in dialog_list if
                is_dialog_type_accepted[dialog["type"]] and dialog["id"] in provided_ids]
    elif len(input_id_lst) > 1:
        provided_ids = [int(dialog_id.replace(",", "")) for dialog_id in input_id_lst]
        return [dialog["id"] for dialog in dialog_list if
                is_dialog_type_accepted[dialog["type"]] and dialog["id"] in provided_ids]


def msg_limit_input_handler(msg_limit):
    """
    Functions handles msg_limit depending on the input

    :param msg_limit: maximum amount of messages to be
                      downloaded for each dialog
    :return: msg_limit
    """
    msg_limit = 100000000 if msg_limit == -1 else msg_limit
    return msg_limit


def msg_handler(msg):
    """
    Handles attributes of a specific message, depending if
    it is text, photo, voice, video or sticker

    :param msg: message
    :return: dict of attributes
    """
    msg_attributes = {
        "message": msg.message,
        "type": "text",
        "duration": "",
        "to_id": "",
    }

    if hasattr(msg.to_id, "user_id"):
        msg_attributes["to_id"] = msg.to_id.user_id
    else:
        msg_attributes["to_id"] = msg.to_id

    if msg.sticker:
        for attribute in msg.sticker.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeSticker):
                msg_attributes["message"] = attribute.alt
                msg_attributes["type"] = "sticker"

    elif msg.video:
        for attribute in msg.video.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeVideo):
                msg_attributes["duration"] = attribute.duration
                msg_attributes["type"] = "video"

    elif msg.voice:
        for attribute in msg.voice.attributes:
            if isinstance(attribute, telethon.tl.types.DocumentAttributeAudio):
                msg_attributes["duration"] = attribute.duration
                msg_attributes["type"] = "voice"

    elif msg.photo:
        msg_attributes["type"] = "photo"

    return msg_attributes


async def get_message_reactions(message: telethon.types.Message, dialog_peer: telethon.types.InputPeerChat) \
        -> Dict[int, str]:
    """
    Loads reactions for a single message. Doesn't work for broadcast channels.

    :param message: instance of message
    :param dialog_peer: instance of this dialog's peer

    :return: dict of "user_id - reaction emoji" pairs
    """
    try:
        result = await client(telethon.functions.messages.GetMessageReactionsListRequest(
            peer=dialog_peer,
            id=message.id,
            limit=REACTIONS_LIMIT_PER_MESSAGE,
        ))

        reaction_objects = result.reactions
        reactions = {reaction_object.peer_id.user_id: reaction_object.reaction for reaction_object in reaction_objects}

    except telethon.errors.rpcerrorlist.MsgIdInvalidError:
        reactions = {}

    except:
        reactions = None

    return reactions

async def download_dialog(client, id, MSG_LIMIT, config):
    """
    Download messages and their metadata for a specific dialog id,
    and save them in *ID*.csv

    :return: None
    """
    try:
        # print(f"client.get_entity({id})")

        tg_entity = await client.get_entity(id)
        messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)
    except ValueError:
        errmsg = f"No such ID found: #{id}"
        print(errmsg)

        try:
            print("Trying to init through username")

            username = None
            dialog_data_json = f'{config["dialogs_list_folder"]}/{id}.json'

            with open(dialog_data_json) as json_file:
                dialog_data = json.load(json_file)

                if "users" in dialog_data \
                        and len(dialog_data["users"]) == 1 \
                        and "username" in dialog_data["users"][0]:
                    username = dialog_data["users"][0]["username"]

                    print(f"Username: {username}")

                    if username:
                        _ = await client.get_entity(username)
                        tg_entity = await client.get_entity(id)
                        messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)

                        print(f"Done.")
                    else:
                        raise ValueError(errmsg, )
                else:
                    print(f"Error for dialog #{id}")
                    print(dialog_data)
                    return
        except ValueError:
            raise ValueError(errmsg, )

    dialog = []

    for m in messages:
        msg_attrs = msg_handler(m)
        msg_reactions = await get_message_reactions(m, telethon.utils.get_peer(id))

        dialog.append(
            {
                "id": m.id,
                "date": m.date,
                "from_id": m.from_id,
                "to_id": msg_attrs["to_id"],
                "fwd_from": m.fwd_from,
                "message": msg_attrs["message"],
                "type": msg_attrs["type"],
                "duration": msg_attrs["duration"],
                "reactions": msg_reactions,
            }
        )

    dialog_file_path = os.path.join(config["dialogs_data_folder"], f"{str(id)}.csv")

    df = pd.DataFrame(dialog)
    df.to_csv(dialog_file_path)

async def download_dialog_within_batches(client, id, MSG_LIMIT, config):
    """
    Download messages and their metadata for a specific dialog id,
    and save them in *ID*.csv. If a CSV already exists,
    resume from the last message.

    :return: None
    """
    try:
        tg_entity = await client.get_entity(id)
    except ValueError:
        errmsg = f"No such ID found: #{id}"
        print(errmsg)
        return

    dialog_file_path = os.path.join(config["dialogs_data_folder"], f"{str(id)}.csv")
    all_messages = []
    offset_id = None
    batch_size = 10000  # Download 10,000 messages at a time
    total_messages = 0

    if os.path.exists(dialog_file_path) and os.path.getsize(dialog_file_path) > 0:
        print(f"Continuation mode: Found existing CSV for dialog #{id}. Resuming download...")
        df = pd.read_csv(dialog_file_path)
        if not df.empty:
            last_row = df.iloc[-1]
            offset_id = last_row['id']
            total_messages = len(df)
            all_messages = df.to_dict('records')
        print(f"Resuming from message ID: {offset_id}")
    else:
        print(f"Continuation mode:Starting fresh download for dialog #{id}...")

    while total_messages < MSG_LIMIT:
        try:
            print(f"Downloading batch {'starting from message ID: ' + str(offset_id) if offset_id else 'of most recent messages'}")
            messages = await client.get_messages(tg_entity, limit=min(batch_size, MSG_LIMIT - total_messages), offset_id=offset_id)
            
            if not messages:
                break  # No more messages to fetch
            
            new_messages = 0
            for m in messages:
                if offset_id and m.id >= offset_id:
                    continue  # Skip messages we already have
                
                msg_attrs = msg_handler(m)
                msg_reactions = await get_message_reactions(m, telethon.utils.get_peer(id))

                all_messages.append({
                    "id": m.id,
                    "date": m.date,
                    "from_id": m.from_id,
                    "to_id": msg_attrs["to_id"],
                    "fwd_from": m.fwd_from,
                    "message": msg_attrs["message"],
                    "type": msg_attrs["type"],
                    "duration": msg_attrs["duration"],
                    "reactions": msg_reactions,
                })
                new_messages += 1

            total_messages += new_messages
            if messages:
                offset_id = messages[-1].id
            print(f"Downloaded {new_messages} new messages. Total: {total_messages}")

            # Save progress after each batch
            df = pd.DataFrame(all_messages)
            df.to_csv(dialog_file_path, index=False)
            print(f"Saved progress to {dialog_file_path}")

        except Exception as e:
            print(f"Error occurred while downloading batch: {str(e)}")
            break

    print(f"Finished downloading. Total messages: {len(all_messages)}")


if __name__ == "__main__":
    args = init_args()

    CONFIG_PATH = args.config_path
    MSG_LIMIT = msg_limit_input_handler(args.dialog_msg_limit)
    SESSION_NAME = args.session_name
    DEBUG_MODE = args.debug_mode
    CONTINUATION = args.continuation

    is_dialog_type_accepted = {'Private dialog': not args.skip_private,
                               'Group': not args.skip_groups,
                               'Channel': not args.skip_channels}

    config = init_config(CONFIG_PATH)
    dialogs_list = read_dialogs(config["dialogs_list_folder"])
    client = telethon.TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"], system_version="4.16.30-vxCUSTOM")

    DIALOGS_ID = dialogs_id_input_handler(args.dialogs_ids, is_dialog_type_accepted, dialogs_list)

    # Dialogs are the "conversations you have open".
    # This method returns a list of Dialog, which
    # has the .entity attribute and other information.
    # dialogs = client.get_dialogs()

    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)

    if not os.path.exists(config["dialogs_data_folder"]):
        os.mkdir(config["dialogs_data_folder"])

    for id in DIALOGS_ID:
        print(f"Loading dialog #{id}")

        with client:
            if(CONTINUATION):
                client.loop.run_until_complete(download_dialog_within_batches(client, id, MSG_LIMIT, config))
            else:
                client.loop.run_until_complete(download_dialog(client, id, MSG_LIMIT, config, CONTINUATION))
