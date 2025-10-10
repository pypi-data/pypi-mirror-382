from itertools import permutations
from typing import Dict, List

import pandas as pd

from ons_metadata_validation.processing.data_structures import Fail
from ons_metadata_validation.processing.validate_funcs import _get_fails


def table_names_must_appear_in_main_tabs(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    keys: List[str],
    fail_type: str,
) -> List[Fail]:
    # remove completely blank sheets from validation
    # mainly considering the permanently empty Codes and Values sheet
    keys = [key for key in keys if len(xl[template_map[key]["tab"]]) != 0]

    gcp_bq_series = [xl[template_map[key]["tab"]][key] for key in keys]
    series_df_combos = list(permutations(gcp_bq_series, 2))

    fails = []

    for src_series, tgt_series in series_df_combos:
        fails.extend(
            _get_fails(
                template_map[tgt_series.name],
                tgt_series[~tgt_series.isin(src_series)],
                fail_type,
                "table_must_appear_on_DatasetFile_DatasetSeries_and_Variables",
            )
        )
    return fails


def must_not_have_duplicate_values(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    keys: List[str],
    fail_type: str,
) -> List[Fail]:
    fails = []

    for key in keys:
        tab = template_map[key]["tab"]
        series = xl[tab][key]
        series = series[series.ne("")]
        fails.extend(
            _get_fails(
                template_map[key],
                series[series.duplicated(keep=False)],
                fail_type,
                "must_not_have_duplicate_values",
            )
        )
    return fails


def must_have_unique_values_in_group(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    keys: List[str],
    fail_type: str,
    groupby_col: str,
) -> List[Fail]:
    fails = []
    tab = template_map[groupby_col]["tab"]
    for series_name, records in xl[tab].groupby(groupby_col):
        for key in keys:
            series = records[key]
            fails.extend(
                _get_fails(
                    template_map[key],
                    series[series.duplicated(keep=False)],
                    fail_type,
                    f"must_not_have_duplicate_values_in_group_{series_name}",
                )
            )
    return fails


def number_of_dataset_entries_must_match(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    keys: List[str],
    fail_type: str,
) -> List[Fail]:
    value_tab = template_map[keys[0]]["tab"]
    value_name = template_map[keys[0]]["name"]
    reported_value = xl[value_tab][keys[0]]

    len_tab = template_map[keys[1]]["tab"]
    actual_value = len(xl[len_tab][keys[1]])

    fails = []
    fails.extend(
        _get_fails(
            template_map[keys[0]],
            reported_value[reported_value != actual_value],
            fail_type,
            f"{value_name}_does_not_match_number_of_entries_on_tab_{len_tab}",
        )
    )

    return fails


def must_not_match_other_field(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    keys: List[str],
    fail_type: str,
) -> List[Fail]:
    first_field = template_map[keys[0]]
    first_field_value = xl[first_field["tab"]][keys[0]]

    second_field = template_map[keys[1]]
    second_field_value = xl[second_field["tab"]][keys[1]]

    fails = []
    fails.extend(
        _get_fails(
            template_map[keys[0]],
            first_field_value[first_field_value == second_field_value],
            fail_type,
            f"{first_field['name']}_must_not_match_value_in_{second_field['name']}",
        )
    )
    return fails


def must_have_at_least_one_record(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    keys: List[str],
    fail_type: str,
) -> List[Fail]:
    fails = []

    for key in keys:
        if len(xl[template_map[key]["tab"]]) == 0:
            fails.append(
                Fail(
                    fail_type,
                    template_map[key]["tab"],
                    template_map[key]["name"],
                    "No records",
                    f"{template_map[key]['tab']}_tab_must_have_at_least_one_record",
                    cell_ref=template_map[key]["value_cell"],
                )
            )
    return fails
