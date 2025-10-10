import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd
from openpyxl import Workbook


def setup_logger(log_folder: str, level: str) -> bool:
    """basic setup function

    Args:
        file (str): the dunder method __file__ for the initialising file
        idx (int): the number of folder levels to the logging.ini file

    Returns:
        bool: always True!
    """
    logging_level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }
    os.makedirs(log_folder, exist_ok=True)
    logging.basicConfig(
        handlers=[
            RotatingFileHandler(
                f"{log_folder}/{level}.log", maxBytes=5_000_000, backupCount=1
            )
        ],
        format="%(asctime)s :: %(levelname)-8s :: [%(filename)s:%(lineno)-3s - %(funcName)-32s] :: %(message)s",
        level=logging_level[level],
    )
    return True


def compress_logging_value(item: type):
    """compresses the larger logging values

    Args:
        item (type): the item for logging

    Returns:
        type: the compressed value for logging (if necessary)
    """
    if isinstance(item, (bool, int, float, str)):
        return item
    if isinstance(item, pd.DataFrame):
        return item.info()
    if isinstance(item, Workbook):
        return f"Workbook.sheetnames: {item.sheetnames}"
    if isinstance(item, (Sequence, Mapping)):
        if len(item) > 10:
            return f"{type(item)}: len({len(item)})"
        return item
    return item


def get_dir_path(src: str, idx: int, dst: str) -> str:
    """converts a local file path to a relative one

    Args:
        src (str): the current location
        idx (int): the number of folder levels to go up or down
        dst (str): the destination location

    Returns:
        str: the file path as a string
    """
    curr_dir = Path(src).parents[idx]
    return str(curr_dir.joinpath(dst)).replace("\\", "/")
