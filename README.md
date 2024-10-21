# Telegram data collector v0.01
Combination of tools to download your telegram data.


### Structure
##### 0_download_dialogs_list.py
Download dialogs meta data for account.

`--dialogs_limit`
number of dialogs

`-h`
show this help message and exit

`--config_path`
path to config file

`--debug_mode`
Debug mode

`--skip_progress`
Download all messages from scratch, ignoring any previously downloaded data. If not set, the script will check for existing `.csv` files in the `../data/dialogs` folder. It will then download any new messages since the last download, followed by older messages starting from the oldest message in the existing CSV file.
`--all_at_once`
Download all messages all at once instead of in batches of 10,000 messages
##### 1_download_dialogs_data.py
Download all messages from the dialogs.

Use flags `--skip_private`, `--skip_groups`, and `--skip_channels`
to skip private chats, groups, and channels respectively.

### Requirements
Python 3.8.13


### How to run
0. create virtual env
```python -m venv .venv```
1. activate virtual env
```. .venv/bin/activate```
2. install dependencies 
```pip install -r requirements.txt```
3. get your credentials https://my.telegram.org/apps
4. set credentials (api_id, api_hash) in *config/config.json* (can be based on the *config_example.json*)

### How to start
0. ```python 0_download_dialogs_list.py --dialogs_limit -1```
1. ```python 1_download_dialogs_data.py --dialogs_ids -1 --dialog_msg_limit -1```