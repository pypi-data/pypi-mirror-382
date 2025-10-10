import logging
import re
import string
from collections import defaultdict
from copy import deepcopy
from typing import Any, Dict, List, Tuple, Union

import pandas as pd
from openpyxl import Workbook

from ons_metadata_validation.processing.data_structures import TabDetails
from ons_metadata_validation.reference.constants import TAB_DETAILS, SheetMapper
from ons_metadata_validation.reference.delta_table import DELTA_TABLE
from ons_metadata_validation.reference.template import V1_TEMPLATE, V2_TEMPLATE
from ons_metadata_validation.utils.logger import (
    compress_logging_value,
)

logger = logging.getLogger()


def can_cast_to(value: Any, dtype: type) -> bool:
    """record the rows that can be cast to type.

    Args:
        value (Any): the value to attempt casting
        dtype (type): the datatype to cast to

    Returns:
        bool.
    """
    try:
        dtype(value)
        return True
    except (TypeError, ValueError):
        return False


def get_excel_ref_components(cell_ref: str) -> Tuple[str, int]:
    """Convert cell reference to it's components. E.G. "C14" -> ("C", 14).

    Args:
        cell_ref (str): The excel reference

    Returns:
        Tuple[str, int]: the letter and number components.
    """
    match = re.match(r"^([A-Z]+)(\d+)$", cell_ref)
    letters = match.group(1)
    numbers = match.group(2)
    return letters, int(numbers)


def write_dfs_to_wb(
    template_map: Dict,
    xl: Dict[str, pd.DataFrame],
    wb: Workbook,
) -> bool:
    """Populate a metadata wb with modified xl values.

    Args:
        wb (Workbook): Empty workbook to populate.
        xl (Dict[str, pd.DataFrame]): The modified xl structure
        template_map (Dict): the template map for the metadata version.

    Returns:
        bool: If the process was successful.
    """
    exceptions = []
    for tab in SheetMapper._value2member_map_.keys():
        if tab not in xl:
            continue
        for col in xl[tab].columns:
            # this is for avoiding "Change history" being flagged
            if col not in template_map:
                continue
            try:
                letters, numbers = get_excel_ref_components(
                    template_map[col]["value_cell"]
                )
                for idx, val in enumerate(xl[tab][col]):
                    wb[template_map[col]["tab"]][f"{letters}{numbers + idx}"] = val
            except Exception as e:
                exceptions.append(f"{e} for tab: {tab}, col {col}")

    if exceptions:
        print(exceptions)

        return False
    return True


def xl_column_to_pd_index(excel_column_letter: str) -> int:
    """Convert Excel Column Letter to Pandas Column Position.

    Args:
        excel_column_letter (str): Excel Column Letter (e.g. 'A')

    Returns:
        int: Pandas Column Position
    """
    num = 0
    for c in excel_column_letter:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord("A")) + 1
    return num - 1


def xl_cell_ref_to_pd_index(excel_cell_ref: str) -> Tuple[int, int]:
    """Convert Excel Cell Reference into Pandas Row & Column position.

    Args:
        excel_cell_ref (str): Excel Cell Address (e.g. 'A1')

    Raises:
        ValueError: If excel_cell_ref isn't Excel cell address.

    Returns:
        Tuple[int, int]: Row Position, Column Position.
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    match = re.match(r"^([a-z]+)(\d+)$", excel_cell_ref.lower())
    column = xl_column_to_pd_index(match.group(1))
    row = int(match.group(2)) - 1

    return row, column


def apply_version_changes(
    template_map: Dict, delta_table: Dict, target_version: float
) -> Dict[str, Dict[str, Any]]:
    """sequentially apply changes for metadata version changes.

    Args:
        template_map (Dict): The version template map
        delta_table (Dict): The delta table with changes between versions.
        target_version (str).

    Returns:
        Dict[str, Dict[str, Any]]: The modified template map.
    """
    template_map = deepcopy(template_map)
    # we're not worrying about double digit minor versions or patch versions
    for version in sorted(delta_table.keys()):
        if float(version) > float(target_version):
            continue
        for key, changes in delta_table[version].items():
            if changes is None:
                template_map.pop(key)
            elif key in template_map:
                for cell_attr, attr_value in changes.items():
                    template_map[key][cell_attr] = attr_value
            else:
                template_map[key] = changes
    return template_map


def get_template_map(
    inp_version: str,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, TabDetails]]:
    """gets the template map and tab details for the relevant version.

    Args:
        version (str): the target version.

    Returns:
        Tuple[Dict[str, Dict[str, Any]], Dict[str, TabDetails]].
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    version = float(re.sub(r"[A-Za-z _]", "", inp_version))
    if version not in [1, 2, *list(DELTA_TABLE.keys())]:
        raise ValueError(f"{inp_version} not in DELTA_TABLE keys: {DELTA_TABLE.keys()}")

    if version == 1:
        return V1_TEMPLATE, TAB_DETAILS.get(1, TAB_DETAILS[2])

    template_map = apply_version_changes(V2_TEMPLATE, DELTA_TABLE, version)
    # default get TAB_DETAILS[2] meaning that there are no changes
    return template_map, TAB_DETAILS.get(version, TAB_DETAILS[2])  # type: ignore


def create_tab_maps(
    template_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, str]]:
    """create the renaming map for each of the tabs to our internal references.

    Args:
        template_map (Dict[str, Dict[str, Any]]).

    Returns:
        Dict[str, Dict[str, str]]: dict with keys tab: renaming_map_for_tab
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    new_map = defaultdict(dict)
    for node in template_map.values():
        if node is None:
            continue
        new_map[node["tab"]][node["name"]] = node["std_name"]
    return dict(new_map)


def validate_metadata_structure(
    template_map: Dict[str, Dict[str, Any]],
    xl: Union[Workbook, Dict[str, pd.DataFrame]],
) -> None:
    """validate the metadata structure againsted expected.

    Args:
        template_map (Dict[str, Dict[str, Any]]): The template map for this version.
        xl (Dict[str, pd.DataFrame]): the unfiltered xl template.

    Raises:
        ValueError: raised if there are any mismatches.
    """
    mismatches = []

    for node in template_map.values():
        if node is None:
            continue
        tab = node["tab"]
        expected_name = node["name"]
        xl_ref = node["ref_cell"]

        if isinstance(xl, dict):
            pd_ref = xl_cell_ref_to_pd_index(xl_ref)
            try:
                actual_name = xl[tab].iloc[pd_ref]
            except IndexError as e:
                mismatches.append(
                    f"Expected {expected_name} on {tab} at ref {xl_ref}. Got {e}"
                )

        if isinstance(xl, Workbook):
            try:
                actual_name = xl[tab][xl_ref].value
            except IndexError as e:
                mismatches.append(
                    f"Expected {expected_name} on {tab} at ref {xl_ref}. Got {e}"
                )

        if actual_name != expected_name:
            mismatches.append(
                f"Expected {expected_name} on {tab} at ref {xl_ref}. Got {actual_name}"
            )

    if mismatches:
        raise ValueError(f"Excel does not match expected structure: {mismatches}")


def records_to_json(
    records: List[Dict[str, Any]], key_col: str
) -> Dict[str, Dict[str, Any]]:
    return {node[key_col]: node for node in records}


def collapse_df(df: pd.DataFrame, groupby_col: str) -> Dict[str, List[Dict[str, Any]]]:
    return {
        k: group.convert_dtypes().fillna("").to_dict("records")
        for k, group in df.groupby(groupby_col)
    }  # type: ignore


def is_nullable(item: str) -> bool:
    return item.strip().upper() == "NULL"
