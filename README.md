# Telegram insights v0.01
Combination of tools to download your telegram data.


  
## Todo
#### Inprog
[J] 2.3. We download single dialog by ID now, this logic should be done for 3 different inputs:
a)single dialog id (current logic), input "1"
b)coma separated list of ids, input "1,2,3"
c)download msgs from all dialogs, input "-1"


#### Backlog
2. [1_dialog_data_manager.py] - 35%


1. [0_download_dialogs_meta_data.py] - 60%
1.1. [0_download_dialogs_meta_data.py] Create data/meta folder if not exists
1.2. [0_download_dialogs_meta_data.py] Fix problem with cyrillic encoding in save_dialog()
1.3. [0_download_dialogs_meta_data.py] Fix downloading of users list, only exception branch works now 
1.4. [0_download_dialogs_meta_data.py] Add proper exception (Andrew)
1.5. [0_download_dialogs_meta_data.py] Refactoring

3. Documentation - 85%
3.1 Download diagram from draw.io

4. Remove msg data from repo.

#### Done:
2.1. [J] [1_dialog_data_manager.py] Show list of all dialogs (read from data/meta)
2.1.1. BUG in the [1_dialog_data_manager.py] `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc9` appears after running the code.
2.1.2. BUG in the [1_dialog_data_manager.py] `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` appears after using "encoding" argument for "open()" 
2.3. [J] [1_dialog_data_manager.py] Read dialogs in the list(example "dialogs_list"), each list element should be dict with dialog meta data.
`a=[]
el = {"a":1,"b":2}
a.append(el)`
2.4. [J] [1_dialog_data_manager.py] Print "dialogs_list" as table with columns in the terminal.

0. Delete session from git tmp.session (Andrew handover)

2.2.1. Get input arguments:
a)show_dialogs INT
b)download_dialog INT
logic can be copied from the [0_download_dialogs_meta_data.py]

2.2. [A] [1_dialog_data_manager.py] Download dialog by ID
2.2.2. If input show_dialogs is >0, show number of dialogs defined in the argument value
2.2.3. If input download_dialog is not empty show
"Download dialog with id #{value}"
## Documentation

### Structure
##### 0_download_dialogs_meta_data.py
Download dialogs meta data for account.

`--dialogs_limit`
number of dialogs

`-h`
show this help message and exit

`--config_path`
path to config file

`--debug_mode`
Debug mode



### How to run
0. get your credentials https://my.telegram.org/apps
1. set credentials (api_id, api_hash) in *config/config.json* (can be based on the *config_example.json*)
