# download_dialogs_list.py

import argparse
import os
import json
import logging
from typing import Any, List, Dict

from telethon import TelegramClient
from telethon.errors import RPCError

from utils.config import init_config, setup_logging

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn

import asyncio


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Download dialogs list for a Telegram user."
    )
    parser.add_argument(
        "--dialogs_limit",
        type=int,
        default=-1,
        help="Number of dialogs to download. Use -1 for all."
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


def save_dialog_metadata(dialog: Any, folder: str, participants: List[Dict[str, Any]]) -> None:
    """
    Save dialog metadata to a JSON file.

    :param dialog: Dialog object from Telethon.
    :param folder: Folder path to save the dialog metadata.
    :param participants: List of participants in the dialog.
    """
    metadata = {
        "id": dialog.id,
        "name": dialog.name,
        "type": get_dialog_type(dialog),
        "users": participants
    }

    dialog_file_path = os.path.join(folder, f"{dialog.id}.json")
    try:
        with open(dialog_file_path, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
        logging.info(f"Saved dialog metadata to {dialog_file_path}")
    except IOError as e:
        logging.error(f"Failed to save dialog {dialog.id}: {e}")


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


async def get_dialog_users(client: TelegramClient, dialog: Any) -> List[Dict[str, Any]]:
    """
    Retrieve users in the dialog.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :return: List of user dictionaries.
    """
    users = []
    try:
        participants = await client.get_participants(dialog)
        for user in participants:
            if user.username:
                users.append({
                    "user_id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "phone": user.phone,
                })
    except RPCError as e:
        logging.warning(f"Failed to get participants for dialog {dialog.id}: {e}")
    return users


async def download_and_save_dialog(client: TelegramClient, dialog: Any, folder: str, progress: Progress, task_id: int) -> None:
    """
    Download a single dialog and save its metadata.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :param folder: Folder path to save dialog metadata.
    :param progress: Rich Progress instance.
    :param task_id: Task ID for the progress bar.
    """
    try:
        participants = await get_dialog_users(client, dialog)
        save_dialog_metadata(dialog, folder, participants)
        progress.update(task_id, advance=1, description=f"[green]Completed: {dialog.name}")
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


async def download_and_save_dialogs(client: TelegramClient, limit: int, folder: str, concurrency: int) -> None:
    """
    Download dialogs and save their metadata with concurrency control and progress bars.

    :param client: Authenticated TelegramClient instance.
    :param limit: Maximum number of dialogs to download.
    :param folder: Folder path to save dialog metadata.
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
        # Initialize Rich Progress with a master progress bar and individual dialog progress bars
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=Console()
        )

        # Determine total number of dialogs
        if effective_limit is None:
            # Fetch all dialogs to determine the total count
            logging.info("Fetching all dialogs to determine total count...")
            all_dialogs = await client.get_dialogs()
            total_dialogs = len(all_dialogs)
            dialogs = all_dialogs
            logging.info(f"Total dialogs found: {total_dialogs}")
            task_description = "Downloading all dialogs..."
        else:
            # Fetch limited number of dialogs
            dialogs = []
            async for dialog in client.iter_dialogs(limit=effective_limit):
                dialogs.append(dialog)
            total_dialogs = len(dialogs)
            task_description = f"Downloading {total_dialogs} dialogs..."

        with progress:
            overall_task = progress.add_task(task_description, total=total_dialogs)
            tasks = []

            for dialog in dialogs:
                await semaphore.acquire()
                if progress.finished:
                    semaphore.release()
                    break

                # Create a new task for each dialog
                task_id = progress.add_task(f"[yellow]Processing: {dialog.name}", total=1)
                task = asyncio.create_task(
                    process_dialog(client, dialog, folder, progress, task_id, semaphore)
                )
                tasks.append(task)
                progress.update(overall_task, advance=1)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

    except RPCError as e:
        logging.error(f"Failed to download dialogs: {e}")


async def process_dialog(client: TelegramClient, dialog: Any, folder: str, progress: Progress, task_id: int, semaphore: asyncio.Semaphore) -> None:
    """
    Wrapper to process a dialog and handle semaphore release.

    :param client: Authenticated TelegramClient instance.
    :param dialog: Dialog object from Telethon.
    :param folder: Folder path to save dialog metadata.
    :param progress: Rich Progress instance.
    :param task_id: Task ID for the progress bar.
    :param semaphore: Semaphore to control concurrency.
    """
    try:
        await download_and_save_dialog(client, dialog, folder, progress, task_id)
    finally:
        # Schedule the removal of the task after a short delay to keep active dialogs at the top
        asyncio.create_task(remove_task_after_delay(progress, task_id))
        semaphore.release()


def main():
    args = parse_arguments()

    # Init config
    try:
        config = init_config(args.config_path)
    except FileNotFoundError as e:
        logging.error(e)
        return
    
    # Determine the logging level
    if args.debug:
        log_level = "DEBUG"
    else:
        log_level = args.log_level
    
    # Determine log file name
    os.makedirs(config['logs_folder'], exist_ok=True)
    log_file = os.path.join(config['logs_folder'], "download_dialogs_list.log")

    setup_logging(log_level, log_file=log_file)

    try:
        config = init_config(args.config_path)
    except FileNotFoundError as e:
        logging.error(e)
        return

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
            download_and_save_dialogs(
                client,
                limit,
                config["dialogs_list_folder"],
                concurrency
            )
        )


if __name__ == "__main__":
    main()
