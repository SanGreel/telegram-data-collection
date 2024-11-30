# Telegram data collector v0.02

Combination of Python scripts that allow to download data from Telegram, consisting from all dialog metadata (names, members, etc.) and messages from those chats.

## Structure

This repo consists of two parts:

1. ### Main repo Python code

    [`telegram_data_downloader`](telegram_data_downloader) directory consists of the main Python code that drive the [scripts](#scripts).

    A few words about underlying modules:

    1. [`dict_types`](/telegram_data_downloader/dict_types) contains basic type definitions for the data structures that are used throughout other modules.

    1. [`loader`](/telegram_data_downloader/loader) contains files to manage reading and writing metadata and message data. Currently this data is exported to local filesystem.

    1. [`processor`](/telegram_data_downloader/processor) contains files to manage the processing and downloading of the data.

    1. [`settings`](/telegram_data_downloader/settings.py) is responsible for initializing the settings and configuration for the downloader. It also contains some important constants, about which you can read more in the file itself.

1. ### Scripts

    These scripts are the main entrypoint and perform dialog metadata and message downloading.

    There are two scripts:

    1. [`0_download_dialogs_list.py`](/0_download_dialogs_list.py)

        This script downloads the metadata of all dialogs for the account.
        Run with `-h` to see the available options.

    1. [`1_download_dialogs_data.py`](/1_download_dialogs_data.py)

        This script downloads all messages from the dialogs.
        Run with `-h` to see the available options.

    We _strongly_ encourage you to read the help of the scripts and visit settings file to understand the available options.

## Requirements

- Python 3.11^
- pip

## Installation

1. Clone the repository

    ```bash
    git clone <repo-url>
    cd telegram-data-collection
    ```

1. Install package manager used by the project - [Poetry](https://python-poetry.org/)

    ```bash
    python3.11 -m pip install poetry
    ```

1. Install dependencies

    ```bash
    poetry install --without=dev
    ```

    In case you want to install the virtual environment in current directory and not in the default Poetry location (you can more about it [here](https://python-poetry.org/docs/configuration/#virtualenvsin-project)), you can run:

    ```bash
    POETRY_VIRTUALENVS_IN_PROJECT=true poetry install --without=dev
    ```

1. Copy [`.env.sample`](/.env.sample) to `.env` and fill in the required values

    ```bash
    cp .env.sample .env
    ```

    For basic usage, you only need to fill in the `API_ID` and `API_HASH` values. These can be obtained from [my.telegram.org](https://my.telegram.org/apps).

    _NOTE_: for detailed information on the message downloading progress, set "LOG_LEVEL" variable to "DEBUG". This allows the logs to include messages on per-chat downloading progress.

## Usage

1. Activate the virtual environment

    ```bash
    poetry shell
    ```

1. Run the scripts

    ```bash
    python 0_download_dialogs_list.py --dialogs-limit -1
    ```

    ```bash
    python 1_download_dialogs_data.py --dialog-ids -1 --dialog-msg-limit -1
    ```

    <!-- markdownlint-disable-next-line MD038 -->
    Note: in case you want to provide dialog ids and you need to enter a negative value for chat id, start your value with `" <your values>"` (enter value in quotes and add a whitespace at the start).
    E.g. `--dialog-ids " -1234567890"`.

## Contributing

If you want to contribute to the project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

In case you were a part of the project and weren't listed as contributor, please let us know.
