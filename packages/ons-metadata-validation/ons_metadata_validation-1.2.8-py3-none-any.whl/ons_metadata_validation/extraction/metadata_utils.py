import os
import re
from typing import List, Union

import pandas as pd


def get_big_query_name(path: str, use_folder: bool = True) -> str:
    if use_folder:
        return os.path.dirname(path).replace("\\", "/").split("/")[-1]
    return os.path.splitext(os.path.basename(path))[0].split(".")[0]


def get_dataset_series_name(item: str) -> str:
    return item.replace("_", " ").title()


def is_nullable_bool(item: bool) -> str:
    if item:
        return "NULL"
    return "NOT NULL"


def is_nullable(item: Union[bool, str]) -> str:
    if isinstance(item, str):
        if item.upper() in ["NULL", "NOT NULL"]:
            return item.upper()
    if pd.isnull(item):
        return "NULL"
    if isinstance(item, bool):
        return is_nullable_bool(item)
    return ""


def get_file_format(path: str) -> str:
    file_format = ".".join(path.split(".")[1:]).upper()
    return file_format.replace("SNAPPY.", "")


def get_duplicates(inp_list: List[str]) -> List[str]:
    return [i for i in set(inp_list) if inp_list.count(i) > 1]


def is_duplicated(item: str, duplicated_items: List) -> str:
    if item in duplicated_items:
        return "Yes"
    return "No"


def get_length_precision(item: str) -> str:
    if "decimal(" in item.lower():
        return re.search(r"\((.*?)\)", item).group(1)
    return ""


def remove_decimal_precision(item: str) -> str:
    pattern = r"decimal\s*\(\s*\d+\s*,\s*\d+\s*\)"
    return re.sub(pattern, "decimal", item)


def get_date_format(item: str) -> str:
    if item.lower() == "date":
        return "yyyy-MM-dd"
    if item.lower() == "timestamp":
        return "yyyy-MM-dd HH:mm:ss"
    return ""
