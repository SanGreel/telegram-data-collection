"""
This script is a Shell entrypoint, used for invoking classes for downloading messages
from Telegram dialogs.
"""

import argparse
from typing import Callable

import telethon

from telegram_data_downloader import settings
from telegram_data_downloader.dict_types.dialog import DialogMetadata, DialogType
from telegram_data_downloader.factory import (
    create_json_dialog_reader_writer,
    create_message_downloader,
    create_telegram_client,
)


class UninitializedTakeoutSessionException(Exception):
    """
    Exception raised when the `takeout` session is not initialized.
    """


def init_args() -> argparse.Namespace:
    """
    Parse command line arguments for the script and return them.
    """
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
    """
    Filter the dialogs from `dialog_list` based on two conditions:
    1. The dialog type is accepted by the `is_dialog_type_accepted` dict.
    2. The dialog id is in the `input_id_lst`.

    As a parameter to `input_id_lst`, you can provide ["-1"] to download all dialogs.
    """
    is_dialog_included: Callable[[DialogMetadata], bool] = lambda dialog: True  # noqa: E731

    if input_id_lst[0] == "-1":
        pass  # special case to exit early
    elif len(input_id_lst) == 1:
        provided_ids = [int(dialog_id) for dialog_id in input_id_lst[0].split(",")]
        is_dialog_included = lambda dialog: dialog["id"] in provided_ids  # pylint: disable=C3001  # noqa: E731
    elif len(input_id_lst) > 1:
        provided_ids = [int(dialog_id.replace(",", "")) for dialog_id in input_id_lst]
        is_dialog_included = lambda dialog: dialog["id"] in provided_ids  # pylint: disable=C3001  # noqa: E731

    return [
        dialog
        for dialog in dialog_list
        if is_dialog_type_accepted[dialog["type"]] and is_dialog_included(dialog)
    ]


if __name__ == "__main__":
    print("start downloading dialogs...")

    args = init_args()

    MSG_LIMIT = 100_000_000 if args.dialog_msg_limit == -1 else args.dialog_msg_limit
    SESSION_NAME = args.session_name

    dialog_type_to_accepted = {
        DialogType.PRIVATE: not args.skip_private,
        DialogType.GROUP: not args.skip_groups,
        DialogType.CHANNEL: not args.skip_channels,
    }
    print(f"dialog types to download: {dialog_type_to_accepted}")

    dialog_reader = create_json_dialog_reader_writer()
    dialogs = dialog_reader.read_all_dialogs()
    print(f"total dialogs: {len(dialogs)}")
    filtered_dialogs = filter_input_dialogs(
        args.dialog_ids, dialog_type_to_accepted, dialogs
    )
    print(f"total filtered dialogs: {len(filtered_dialogs)}")

    client = create_telegram_client(SESSION_NAME)
    print("downloading dialogs...")
    with client:
        try:
            with client.takeout(
                finalize=settings.CLIENT_TAKEOUT_FINALIZE,
                contacts=settings.CLIENT_TAKEOUT_FETCH_CONTACTS,
                users=settings.CLIENT_TAKEOUT_FETCH_USERS,
                chats=settings.CLIENT_TAKEOUT_FETCH_GROUPS,
                megagroups=settings.CLIENT_TAKEOUT_FETCH_MEGAGROUPS,
                channels=settings.CLIENT_TAKEOUT_FETCH_CHANNELS,
                files=settings.CLIENT_TAKEOUT_FETCH_FILES,
            ) as takeout:
                message_downloader = create_message_downloader(takeout)
                takeout.loop.run_until_complete(
                    message_downloader.download_dialogs(filtered_dialogs, MSG_LIMIT)
                )
        except telethon.errors.TakeoutInitDelayError as e:
            raise UninitializedTakeoutSessionException(
                "\nWhen initiating a `takeout` session, Telegram requires a cooling period "
                "between data exports.\n"
                f"Initial message: {e}\n"
                "Workaround: You can allow takeout by:\n"
                "1. Opening Telegram service notifications (where you retrieved the login code)\n"
                '2. Click allow on "Data export request"\n'
            ) from e
    print("dialogs downloaded")
