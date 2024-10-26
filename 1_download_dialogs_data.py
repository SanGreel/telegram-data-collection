import argparse
from typing import Callable

from telegram_data_downloader.dict_types.dialog import DialogMetadata, DialogType
from telegram_data_downloader.factory import (
    create_json_dialog_reader_writer,
    create_message_downloader,
    create_telegram_client,
)


def init_args():
    parser = argparse.ArgumentParser(description="Step #2. Download dialogs")

    parser.add_argument(
        "--dialog-ids",
        nargs="+",
        type=str,
        help="id(s) of dialog(s) to download, -1 for all",
        required=True,
    )
    parser.add_argument(
        "--dialog-msg-limit",
        type=int,
        help="amount of messages to download from a dialog, -1 for all",
        default=10000,
    )
    parser.add_argument("--session-name", type=str, help="session name", default="tmp")
    parser.add_argument("--skip-private", action="store_true")
    parser.add_argument("--skip-groups", action="store_true")
    parser.add_argument("--skip-channels", action="store_true")

    return parser.parse_args()


def filter_input_dialogs(
    input_id_lst: list[str],
    is_dialog_type_accepted: dict[DialogType, bool],
    dialog_list: list[DialogMetadata],
) -> list[DialogMetadata]:
    condition: Callable[[DialogMetadata], bool] = lambda dialog: True  # noqa: E731

    if input_id_lst[0] == "-1":
        condition = condition  # don't change anything
    elif len(input_id_lst) == 1:
        provided_ids = [int(dialog_id) for dialog_id in input_id_lst[0].split(",")]
        condition = lambda dialog: dialog["id"] in provided_ids  # noqa: E731
    elif len(input_id_lst) > 1:
        provided_ids = [int(dialog_id.replace(",", "")) for dialog_id in input_id_lst]
        condition = lambda dialog: dialog["id"] in provided_ids  # noqa: E731

    return [
        dialog
        for dialog in dialog_list
        if is_dialog_type_accepted[dialog["type"]] and condition(dialog)
    ]


if __name__ == "__main__":
    print("start downloading dialogs...")

    args = init_args()

    MSG_LIMIT = 100_000_000 if args.dialog_msg_limit == -1 else args.dialog_msg_limit
    SESSION_NAME = args.session_name

    is_dialog_type_accepted = {
        DialogType.PRIVATE: not args.skip_private,
        DialogType.GROUP: not args.skip_groups,
        DialogType.CHANNEL: not args.skip_channels,
    }
    print(f"dialog types to download: {is_dialog_type_accepted}")

    dialog_reader = create_json_dialog_reader_writer()
    dialogs = dialog_reader.read_all_dialogs()
    print(f"total dialogs: {len(dialogs)}")
    filtered_dialogs = filter_input_dialogs(
        args.dialog_ids, is_dialog_type_accepted, dialogs
    )
    print(f"total filtered dialogs: {len(filtered_dialogs)}")

    client = create_telegram_client(SESSION_NAME)
    message_downloader = create_message_downloader(client)

    print("downloading dialogs...")
    with client:
        client.loop.run_until_complete(
            message_downloader.download_dialogs(filtered_dialogs, MSG_LIMIT)
        )
    print("dialogs downloaded")
