import json
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

import numpy as np
import openpyxl
import pandas as pd

from ons_metadata_validation.ids_common_utils.metadata_key import (
    METADATAKEY_METAMAPPER_LOOKUP,
    MetadataKey,
)
from ons_metadata_validation.processing.utils import write_dfs_to_wb
from ons_metadata_validation.reference.constants import MetaMapper, SheetMapper
from ons_metadata_validation.reference.template import V2_TEMPLATE


def convert_json_to_v2(json_path: str, v2_path: str, save_path: str) -> bool:
    """Convert ingest json to V2 metadata template.

    Args:
        json_path (str): Path to the metadata JSON.
        v2_path (str): Path to an empty V2 template.
        save_path (str): Where to save the V2 template.

    Raises:
        RuntimeError: If error reading the json.

    Returns:
        bool: Successfully saves wb to excel.
    """
    input_args = locals()
    md_json = read_json(json_path)
    if md_json is None:
        raise RuntimeError(
            f"Unable to read json {json_path}.\nInput args: {json.dumps(input_args, sort_keys=False)}"
        )

    xl = convert_json_to_dfs(md_json)

    try:
        wb = openpyxl.load_workbook(v2_path)
        write_dfs_to_wb(V2_TEMPLATE, xl, wb)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        wb.save(os.path.join(save_path))
        return True
    except Exception as e:
        print(f"{e} for input args: {input_args}")
        return False


def read_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"{e} for {path}")
        return None


def convert_json_to_dfs(md_json: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    md_json_copy = deepcopy(md_json)

    md_series, md_files, md_columns = [], [], []

    for name, raw_series in md_json[MetadataKey.DATA_SERIES.value].items():
        series = deepcopy(raw_series)

        md_files.extend(series.get(MetadataKey.FILES_METADATA.value, []))
        md_columns.extend(
            flatten_columns(series.get(MetadataKey.COLUMNS.value, {}), name)
        )

        try:
            series.pop(MetadataKey.COLUMNS.value)
        except KeyError as e:
            print(f"Unable to pop {MetadataKey.COLUMNS.value}. {e}")

        try:
            series.pop(MetadataKey.FILES_METADATA.value)
        except KeyError as e:
            print(f"Unable to pop {MetadataKey.FILES_METADATA.value}. {e}")

        series[MetadataKey.SERIES_NAME.value] = name
        md_series.append(series)

    try:
        md_json_copy.pop(MetadataKey.DATA_SERIES.value)
    except KeyError as e:
        print(f"Unable to pop {MetadataKey.DATA_SERIES.value}. {e}")

    md_dataset = [md_json_copy]

    xl = {
        SheetMapper.RESOURCE.value: pd.DataFrame(md_dataset).rename(
            columns=METADATAKEY_METAMAPPER_LOOKUP
        ),
        SheetMapper.SERIES.value: pd.DataFrame(md_series).rename(
            columns=METADATAKEY_METAMAPPER_LOOKUP
        ),
        SheetMapper.FILE.value: pd.DataFrame(md_files).rename(
            columns=METADATAKEY_METAMAPPER_LOOKUP
        ),
        SheetMapper.VARS.value: pd.DataFrame(md_columns).rename(
            columns=METADATAKEY_METAMAPPER_LOOKUP
        ),
    }

    strbool_config = [
        (SheetMapper.VARS.value, MetaMapper.VARS_is_primary_key.value, "Yes", "No"),
        (SheetMapper.VARS.value, MetaMapper.VARS_is_foreign_key.value, "Yes", "No"),
        (SheetMapper.VARS.value, MetaMapper.VARS_nullability.value, "NULL", "NOT NULL"),
        (
            SheetMapper.VARS.value,
            MetaMapper.VARS_personally_identifiable_information.value,
            "Yes",
            "No",
        ),
    ]

    for tab, col, true_val, false_val in strbool_config:
        xl[tab][col] = np.where(xl[tab][col], true_val, false_val)

    return xl


def flatten_columns(columns: dict, series_name: str) -> List[Dict]:
    out_cols = []
    for k, v in columns.items():
        v[MetadataKey.COLUMN_SERIES_NAME.value] = series_name
        v[MetadataKey.COLUMN_NAME.value] = k
        out_cols.append(v)
    return out_cols
