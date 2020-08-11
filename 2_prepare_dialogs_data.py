import os
import re
import logging
import argparse
import pandas as pd
from word2number import w2n


def init_tool_config_arg():
    parser = argparse.ArgumentParser(description="Step #3.Prepare dialogs data.")
    parser.add_argument(
        "--dialogs_ids",
        nargs="+",
        type=int,
        help="id(s) of dialog(s) to download, -1 for all",
        required=True,
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="path to config file",
        default="config/config.json",
    )
    parser.add_argument("--debug_mode", type=int, help="Debug mode", default=0)
    return parser.parse_args()


def url_to_domain(word: str, check=False):
    """
    Extracts domain from url.
    :param word: str
    :param check: bool - used to check if given
    string contains url.
    :return: str
    """
    url_extract = re.compile(r'(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)?(?:https?:\/\/)'
                             r'(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)(?:[-a-zA-Z0'
                             r'-9@:%_\+.~#?&//=]*)?')
    if check:
        return url_extract.match(word)
    return url_extract.findall(word)[0]


def word_to_num(word: str) -> str:
    """
    Tries to convert word to number
    works only with English words
    :param word: str
    :return: str
    """
    try:
        num = str(w2n.word_to_num(word))
    except ValueError:
        # logging.debug('Cannot convert word to number.')
        return word
    return num


def delete_symbols(msg: str) -> str:
    """
    Substitutes symbols with spaces.
    :param msg: str
    :return: str
    """
    symbols = re.compile(r"[-!$%^&*()_+|~=`{}\[\]:';<>?,ʼ\/]|[^\w]")
    return re.sub(symbols, ' ', msg)


def clean_message(msg: str) -> str:
    """
    Makes preparation for the given message.
    :param msg: str
    :return: str
    """
    out_msg = []
    for word in str(msg).split():
        if url_to_domain(word, check=True):
            out_msg.append(url_to_domain(word))
        else:
            word = word_to_num(word)
            out_msg.append(delete_symbols(word))
    return re.sub(r'\s\s+', ' ', ' '.join(out_msg))


def prepare_dialogs(dialog_id: str, dialog_path: str, prep_path: str) -> None:
    """
    Reads raw csv data and creates prepared copy
    at /data/prepared_dialogs/
    :param dialog_id: str
    :param dialog_path: str
    :param prep_path: str
    :return: None
    """
    logging.debug(f'Preparing dialog #{dialog_id}.')

    data = pd.read_csv(f'{dialog_path}{dialog_id}.csv')
    for i in data.index:
        data.loc[i, 'message'] = clean_message(data.loc[i, 'message'])
    data.to_csv(f'{prep_path}{dialog_id}.csv')


if __name__ == "__main__":
    args = init_tool_config_arg()

    DIALOG_ID = args.dialogs_ids
    DEBUG_MODE = args.debug_mode
    DIALOG_PATH = 'data/dialogs/'
    PREPARED_PATH = 'data/prepared_dialogs/'

    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)

    if os.path.isdir(DIALOG_PATH):
        if not os.path.isdir(PREPARED_PATH):
            os.mkdir(PREPARED_PATH)

        for dialog in DIALOG_ID:
            prepare_dialogs(dialog, DIALOG_PATH, PREPARED_PATH)
    else:
        logging.error('Dialogs dir does not exist !')
