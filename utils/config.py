# utils/config.py

import os
import json
import logging
from typing import List, Dict

def init_config(config_path: str) -> Dict:
    """
    Initialize configuration from the given JSON file.

    :param config_path: Path to the config file.
    :return: Configuration dictionary.
    :raises FileNotFoundError: If the config file does not exist.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file does not exist. Please create one at {config_path}."
        )

    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    # Ensure necessary directories exist
    ensure_directories([
        config.get("dialogs_data_folder", "data/dialogs_data"),
        config.get("dialogs_list_folder", "data/dialogs_list")
    ])

    # Save updated config if directories were created
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=True)

    return config


def ensure_directories(directories: List[str]) -> None:
    """
    Create directories if they do not exist.

    :param directories: List of directory paths to ensure.
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def setup_logging(log_level: str, log_file: str) -> None:
    """
    Configure logging settings to output only to a log file.

    :param log_level: Logging level as a string (e.g., 'DEBUG', 'INFO').
    :param log_file: Path to the log file.
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(numeric_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
