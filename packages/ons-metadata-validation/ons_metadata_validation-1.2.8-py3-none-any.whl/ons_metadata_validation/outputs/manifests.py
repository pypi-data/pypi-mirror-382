import datetime as dt
import os
from itertools import islice
from typing import Any, Dict, Hashable, Iterable, List

import pandas as pd

from ons_metadata_validation.reference.constants import MetaMapper


def batched(iterable: Iterable, n: int):
    """Adapted from itertools, introduced in python 3.12

    Args:
        iterable (Iterable): the iterable to batch
        n (int): the number of items in a batch

    Yields:
        Generator: generator of lists in batches.
    """
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := list(islice(iterator, n)):
        yield batch


def convert_to_bytes(row: Dict) -> int:
    """convert size from units to bytes.

    Args:
        row (Dict): The row of the DataFrame to convert.

    Returns:
        int: The size in bytes.
    """
    conversions = {
        "B": 1,
        "KB": 1e3,
        "MB": 1e6,
        "GB": 1e9,
        "TB": 1e12,
    }
    size_unit = row[MetaMapper.FILE_file_size_unit.value].upper().strip()
    if size_unit in conversions:
        n_bytes = float(row[MetaMapper.FILE_file_size.value]) * conversions[size_unit]
        return int(n_bytes)
    raise KeyError(f"{size_unit} not a valid size unit")


def get_manifest(
    dataset_file: pd.DataFrame,
    metadata_manifest_entry: Dict[str, str],
    ticket_number: str = "",
    max_files: int = 24,
) -> Dict[Hashable, Any]:
    """Convert the datasets file tab into a manifest file.

    Args:
        dataset_file (pd.DataFrame): The xl tab as a dataframe.

    Returns:
        Dict[Hashable, Any]: The manifest file without the metadata entry.
    """
    now = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    dataset_file = dataset_file.copy()
    dataset_file["file"] = dataset_file[MetaMapper.FILE_file_path_and_name.value].apply(
        os.path.basename
    )
    dataset_file["relativePath"] = dataset_file[
        MetaMapper.FILE_file_path_and_name.value
    ].apply(lambda x: os.path.dirname(x).replace("\\", "/").strip("/"))
    dataset_file["sizeBytes"] = dataset_file[
        [MetaMapper.FILE_file_size.value, MetaMapper.FILE_file_size_unit.value]
    ].apply(lambda x: str(convert_to_bytes(x)), axis=1)
    dataset_file["md5sum"] = dataset_file[MetaMapper.FILE_hash_value_for_checksum.value]
    files: List[Dict[str, str]] = dataset_file[
        ["file", "relativePath", "sizeBytes", "md5sum"]
    ].to_dict("records")  # type: ignore

    manifests = {}

    for idx, batch in enumerate(batched(files, max_files)):
        batch.append(metadata_manifest_entry)
        manifests[f"{now}-{idx}-{ticket_number}.mani"] = {
            "files": batch,
            "headers": "",
        }

    return manifests
