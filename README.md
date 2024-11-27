# Telegram Data Collection V2

This repository is a fork of the original [telegram-data-collection](https://github.com/SanGreel/telegram-data-collection) by SanGreel, created as a gesture of gratitude for the enriching course on Computational Social Sciences. 🙏📚

## What's New? 🚀

This fork introduces several enhancements to elevate the original project's functionality for the future generations of students:
- 🛠️ **Code Refactoring**
- 📊 **Logging**
-  ⚡ **Asynchronous Execution**
- ✨ **Status Bars**
- ⏩ **Execution Speedup** (not sure, need to be confirmed by measurements)


## Project Structure
```
telegram-data-collection-v2/
├── config/
│   └── config.json
├── data_personal/ (will be created after run)
│   ├── dialogs_data/
│   └── dialogs_list/
├── logs/ (will be created after run)
│   ├── download_dialogs_data.log
│   └── download_dialogs_list.log
├── utils/
│   ├── __init__.py
│   └── config.py
├── download_dialogs_list.py
├── download_dialogs_data.py
├── requirements.in
├── requirements.txt
└── README.md
```
## Setup

1. **Clone the repository**:

    ```bash
    git clone https://github.com/mark2002007/telegram-data-collection-v2
    cd telegram-data-collection-v2
    ```

2. **Create a Virtual Environment**

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure**:

    - Create a `config.json` in the `config/` directory with your Telegram API credentials from https://my.telegram.org/apps.

    ```json
    {
        "api_id": "",
        "api_hash": "",
        "dialogs_data_folder": "../data/dialogs",
        "dialogs_list_folder": "../data/dialogs_meta",
        "logs_folder": "./logs"
    }
    ```

## Usage

### 1. Download Dialogs List

```bash
python download_dialogs_list.py --concurrency -1
```

#### **Options:**

- `--dialogs_limit`:  
  **Type:** `int`  
  **Default:** `-1` (Download all dialogs)  
  **Description:** Number of dialogs to download.

- `--config_path`:  
  **Type:** `str`  
  **Default:** `config/config.json`  
  **Description:** Path to the configuration file.

- `--log_level`:  
  **Type:** `str`  
  **Choices:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
  **Default:** `INFO`  
  **Description:** Set the logging level.

- `--debug`:  
  **Action:** `store_true`  
  **Description:** Enable debug mode (sets log level to DEBUG). Overrides `--log_level`.

- `--session_name`:  
  **Type:** `str`  
  **Default:** `tmp`  
  **Description:** Session name for `TelegramClient`.

- `--concurrency`:  
  **Type:** `int`  
  **Default:** `1`  
  **Description:** Number of dialogs to process concurrently. Use `-1` for maximum concurrency based on CPU cores.

### 2. **Download Dialogs Data**

This script downloads messages and reactions for each Telegram dialog.

```bash
python download_dialogs_data.py --concurrency -1
```

#### **Options:**

- `--dialogs_limit`:  
  **Type:** `int`  
  **Default:** `-1` (Download data for all dialogs)  
  **Description:** Number of dialogs to download data from.

- `--config_path`:  
  **Type:** `str`  
  **Default:** `config/config.json`  
  **Description:** Path to the configuration file.

- `--log_level`:  
  **Type:** `str`  
  **Choices:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
  **Default:** `INFO`  
  **Description:** Set the logging level.

- `--debug`:  
  **Action:** `store_true`  
  **Description:** Enable debug mode (sets log level to DEBUG). Overrides `--log_level`.

- `--session_name`:  
  **Type:** `str`  
  **Default:** `tmp`  
  **Description:** Session name for `TelegramClient`.

- `--concurrency`:  
  **Type:** `int`  
  **Default:** `1`  
  **Description:** Number of dialogs to process concurrently. Use `-1` for maximum concurrency based on CPU cores.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

[MIT License](LICENSE)

---