# download_dialogs_data.py

import argparse
import os
import json
import logging
from typing import Any, List, Dict

from telethon import TelegramClient
from telethon.errors import RPCError, FloodWaitError
from telethon.tl.types import InputPeerChannel, PeerChannel

from utils.config import init_config, setup_logging

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn

import asyncio
import pandas as pd


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Download messages and reactions data for Telegram dialogs."
    )
    parser.add_argument(
        "--dialogs_limit",
        type=int,
        default=-1,
        help="Number of dialogs to download data from. Use -1 for all."
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default=os.path.join("config", "config.json"),
        help="Path to the config file."
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)."
    )
    # Retain the --debug flag for backward compatibility
    parser.add_argument(
        "--debug",
        action='store_true',
        help="Enable debug mode (sets log level to DEBUG). Overrides --log_level."
    )
    parser.add_argument(
        "--session_name",
        type=str,
        default="tmp",
        help="Session name for TelegramClient."
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of dialogs to process concurrently (default: 1). Use -1 for maximum concurrency based on CPU cores."
    )
    return parser.parse_args()


def save_dialog_data(dialog_id: int, folder: str, messages: List[Dict[str, Any]], reactions: List[Dict[str, Any]]) -> None:
    """
    Save dialog messages and reactions to CSV files.

    :param dialog_id: ID of the dialog.
    :param folder: Folder path to save the data.
    :param messages: List of message dictionaries.
    :param reactions: List of reaction dictionaries.
    """
    messages_file = os.path.join(folder, f"{dialog_id}_messages.csv")
    reactions_file = os.path.join(folder, f"{dialog_id}_reactions.csv")

    try:
        if messages:
            df_messages = pd.DataFrame(messages)
            df_messages.to_csv(messages_file, index=False, encoding="utf-8")
            logging.info(f"Saved messages to {messages_file}")
        else:
            logging.warning(f"No messages found for dialog {dialog_id}")

        if reactions:
            df_reactions = pd.DataFrame(reactions)
            df_reactions.to_csv(reactions_file, index=False, encoding="utf-8")
            logging.info(f"Saved reactions to {reactions_file}")
        else:
            logging.warning(f"No reactions found for dialog {dialog_id}")

    except Exception as e:
        logging.error(f"Failed to save data for dialog {dialog_id}: {e}")


def get_dialog_type(dialog: Any) -> str:
    """
    Determine the type of the dialog.

    :param dialog: Dialog object from Telethon.
    :return: String representing the dialog type.
    """
    if dialog.is_user:
        return "Private"
    elif dialog.is_group:
        return "Group"
    elif dialog.is_channel:
        return "Channel"
    return "Unknown"


async def get_dialog_reactions(client: TelegramClient, dialog: Any, message_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Retrieve reactions for a list of message IDs in a dialog.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :param message_ids: List of message IDs to fetch reactions for.
    :return: List of reaction dictionaries.
    """
    reactions = []
    try:
        for msg_id in message_ids:
            try:
                msg = await client.get_messages(dialog, ids=msg_id)
                if msg.reactions:
                    for reaction in msg.reactions.results:
                        reactions.append({
                            "message_id": msg_id,
                            "reaction": reaction.reaction,
                            "count": reaction.count
                        })
            except RPCError as e:
                logging.warning(f"Failed to get reactions for message {msg_id} in dialog {dialog.id}: {e}")
    except RPCError as e:
        logging.warning(f"Failed to get reactions for dialog {dialog.id}: {e}")
    return reactions


async def count_messages(client: TelegramClient, dialog: Any) -> int:
    """
    Count the number of messages in a dialog.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :return: Total number of messages in the dialog.
    """
    count = 0
    try:
        async for _ in client.iter_messages(dialog):
            count += 1
    except RPCError as e:
        logging.warning(f"Failed to count messages for dialog {dialog.id}: {e}")
    return count


async def download_and_save_dialog_data(client: TelegramClient, dialog: Any, folder: str, progress: Progress, task_id: int) -> None:
    """
    Download messages and reactions for a single dialog and save them.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :param folder: Folder path to save dialog data.
    :param progress: Rich Progress instance.
    :param task_id: Task ID for the progress bar.
    """
    try:
        total_messages = await count_messages(client, dialog)
        if total_messages == 0:
            logging.warning(f"No messages found for dialog {dialog.id}")
            progress.update(task_id, completed=1, description=f"[red]No messages: {dialog.name}")
            return

        progress.update(task_id, total=total_messages, description=f"[yellow]Downloading: {dialog.name}")

        messages = []
        async for message in client.iter_messages(dialog):
            messages.append({
                "message_id": message.id,
                "date": message.date.isoformat(),
                "sender_id": message.sender_id,
                "text": message.text
            })
            progress.update(task_id, advance=1)

        message_ids = [msg["message_id"] for msg in messages]
        reactions = await get_dialog_reactions(client, dialog, message_ids)

        save_dialog_data(dialog.id, folder, messages, reactions)

        progress.update(task_id, description=f"[green]Completed: {dialog.name}")
    except FloodWaitError as e:
        logging.warning(f"FloodWaitError for dialog {dialog.id}: Sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds + 5)  # Adding a buffer
        await download_and_save_dialog_data(client, dialog, folder, progress, task_id)
    except RPCError as e:
        logging.error(f"RPCError processing dialog {dialog.id}: {e}")
        progress.update(task_id, description=f"[red]RPCError: {dialog.name}", completed=1)
    except Exception as e:
        logging.error(f"Error processing dialog {dialog.id}: {e}")
        progress.update(task_id, description=f"[red]Error: {dialog.name}", completed=1)


async def remove_task_after_delay(progress: Progress, task_id: int, delay: float = 2.0) -> None:
    """
    Remove a progress task after a specified delay.

    :param progress: Rich Progress instance.
    :param task_id: Task ID to remove.
    :param delay: Delay in seconds before removing the task.
    """
    await asyncio.sleep(delay)
    try:
        progress.remove_task(task_id)
    except Exception as e:
        logging.debug(f"Failed to remove task {task_id}: {e}")


async def download_and_save_dialogs_data(client: TelegramClient, limit: int, folder: str, concurrency: int) -> None:
    """
    Download dialogs data and save their messages and reactions with concurrency control and progress bars.

    :param client: Authenticated TelegramClient instance.
    :param limit: Maximum number of dialogs to download data from.
    :param folder: Folder path to save dialog data.
    :param concurrency: Number of dialogs to process concurrently.
    """
    if limit == -1:
        effective_limit = None
    else:
        effective_limit = limit

    if concurrency == -1:
        semaphore = asyncio.Semaphore(os.cpu_count() * 5)  # Maximum concurrency based on CPU cores
    elif concurrency > 0:
        semaphore = asyncio.Semaphore(concurrency)
    else:
        logging.error("Concurrency must be a positive integer or -1 for maximum concurrency.")
        return

    try:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=Console()
        )

        if effective_limit is None:
            logging.info("Fetching all dialogs to determine total count...")
            all_dialogs = await client.get_dialogs()
            total_dialogs = len(all_dialogs)
            dialogs = all_dialogs
            logging.info(f"Total dialogs found: {total_dialogs}")
            task_description = "Downloading all dialogs data..."
        else:
            dialogs = []
            async for dialog in client.iter_dialogs(limit=effective_limit):
                dialogs.append(dialog)
            total_dialogs = len(dialogs)
            task_description = f"Downloading {total_dialogs} dialogs data..."

        with progress:
            overall_task = progress.add_task(task_description, total=total_dialogs)
            tasks = []

            for dialog in dialogs:
                await semaphore.acquire()
                if progress.finished:
                    semaphore.release()
                    break

                task_id = progress.add_task(f"[yellow]Processing: {dialog.name}", total=1)
                task = asyncio.create_task(
                    process_dialog_data(client, dialog, folder, progress, task_id, semaphore)
                )
                tasks.append(task)
                progress.update(overall_task, advance=1)

            await asyncio.gather(*tasks)

    except RPCError as e:
        logging.error(f"Failed to download dialogs data: {e}")


async def process_dialog_data(client: TelegramClient, dialog: Any, folder: str, progress: Progress, task_id: int, semaphore: asyncio.Semaphore) -> None:
    """
    Wrapper to process a dialog's data and handle semaphore release.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :param folder: Folder path to save dialog data.
    :param progress: Rich Progress instance.
    :param task_id: Task ID for the progress bar.
    :param semaphore: Semaphore to control concurrency.
    """
    try:
        await download_and_save_dialog_data(client, dialog, folder, progress, task_id)
    finally:
        asyncio.create_task(remove_task_after_delay(progress, task_id))
        semaphore.release()


def main():
    args = parse_arguments()

    try:
        config = init_config(args.config_path)
    except FileNotFoundError as e:
        logging.error(e)
        return
    
    if args.debug:
        log_level = "DEBUG"
    else:
        log_level = args.log_level

    os.makedirs(config['logs_folder'], exist_ok=True)
    log_file = os.path.join(config['logs_folder'], "download_dialogs_data.log")
    
    setup_logging(log_level, log_file=log_file)

    # Handle --dialogs_limit
    if args.dialogs_limit == -1:
        limit = -1  # No limit
    else:
        limit = args.dialogs_limit

    # Handle --concurrency
    if args.concurrency == -1:
        concurrency = os.cpu_count() * 5  
    else:
        concurrency = args.concurrency

    client = TelegramClient(
        args.session_name,
        config["api_id"],
        config["api_hash"],
        system_version="4.16.30-vxCUSTOM"
    )

    with client:
        client.loop.run_until_complete(
            download_and_save_dialogs_data(
                client,
                limit,
                config["dialogs_data_folder"],
                concurrency
            )
        )


if __name__ == "__main__":
    main()
