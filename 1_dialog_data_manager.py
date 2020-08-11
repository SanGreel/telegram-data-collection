import os
import argparse
import pandas as pd
import logging
from utils.utils import init_config, init_tg_client, read_dialogs, prepare_msg


def init_tool_config_arg():
    parser = argparse.ArgumentParser(description="Step #2.Download dialogs")

    parser.add_argument(
        "--dialogs_ids",
        nargs="+",
        type=int,
        help="id(s) of dialog(s) to download, -1 for all",
        required=True,
    )
    parser.add_argument(
        "--dialog_msg_limit",
        type=int,
        help="amount of messages to download from a dialog",
        default=100,
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default="config/config.json",
    )
    parser.add_argument("--debug_mode", type=int, help="Debug mode", default=0)
    parser.add_argument("--session_name", type=str, help="session name", default="tmp")

    return parser.parse_args()


if __name__ == "__main__":

    args = init_tool_config_arg()

    CONFIG_PATH = args.config_path
    DIALOG_ID = args.dialogs_ids
    MSG_LIMIT = args.dialog_msg_limit
    SESSION_NAME = args.session_name
    DEBUG_MODE = args.debug_mode

    config = init_config(CONFIG_PATH)
    dialogs_list = read_dialogs(config["dialogs_metadata_folder"])

    client = init_tg_client(SESSION_NAME, config["api_id"], config["api_hash"])

    if DIALOG_ID[0] == -1:
        DIALOG_ID = []
        for d in dialogs_list:
            DIALOG_ID.append(d["id"])

    # TODO: add a logic to download all msgs
    if MSG_LIMIT == -1:
        MSG_LIMIT = 100000000

    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)

    for d in DIALOG_ID:
        print(f"dialog #{d}")


        async def download_dialog():

            # TODO: add handler for wrong IDs
            tg_entity = await client.get_entity(d)
            messages = await client.get_messages(tg_entity, limit=MSG_LIMIT)
            logging.debug('Dialogs were downloaded.')
            dialog = []

            for m in messages:
                if hasattr(m.to_id, "user_id"):
                    to_id = m.to_id.user_id
                else:
                    to_id = m.to_id

                dialog.append(
                    {
                        "id": m.id,
                        "date": m.date,
                        "from_id": m.from_id,
                        "to_id": to_id,
                        "fwd_from": m.fwd_from,
                        "message": m.message,
                    }
                )

            dialog_file_path = os.path.join(
                config["dialogs_data_folder"], f"{str(d)}.csv"
            )

            df = pd.DataFrame(dialog)
            df.to_csv(dialog_file_path)


        with client:
            client.loop.run_until_complete(download_dialog())
