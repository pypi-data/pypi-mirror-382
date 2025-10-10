import logging
import re
from typing import Callable, Dict, List, Tuple

import attrs
import pandas as pd
from tqdm import tqdm

from ons_metadata_validation.processing.data_structures import Fail
from ons_metadata_validation.processing.utils import can_cast_to
from ons_metadata_validation.reference.constants import (
    NON_BREAKING_MANDATORY,
    MetaMapper,
    SheetMapper,
)
from ons_metadata_validation.utils.logger import (
    compress_logging_value,
)

logger = logging.getLogger()


def validate_xl_single_values(
    xl: Dict[str, pd.DataFrame],
    template_map: dict,
    validation_map: dict,
    role_skip_config: list,
    fail_types: list = ["hard", "soft"],
    tabs_to_validate: list = [
        SheetMapper.RESOURCE.value,
        SheetMapper.FILE.value,
        SheetMapper.SERIES.value,
        SheetMapper.VARS.value,
        SheetMapper.BACK_OFFICE.value,
    ],
) -> pd.DataFrame:
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    all_fails = []

    for key in tqdm(template_map, "validating single values"):
        if template_map[key] is None:
            # this means it's been removed
            continue

        tab = template_map[key]["tab"]
        if any(
            [
                key in role_skip_config,
                tab not in xl,
                tab not in tabs_to_validate,
                key not in xl[tab].columns,
            ]
        ):
            continue

        unchecked_values = xl[tab][key]

        # catch all the missing values before we dropna
        # only care if the value is mandatory
        missing_values = unchecked_values.apply(lambda x: str(x).strip()).eq("")
        if template_map[key]["mandatory"]:
            all_fails.extend(
                _get_fails(
                    template_map[key],
                    unchecked_values[missing_values],
                    "hard" if key not in NON_BREAKING_MANDATORY else "soft",
                    "missing_value",
                )
            )
        unchecked_values = unchecked_values[~missing_values]

        # catch all the values that we can't cast to the expected type
        dtype = template_map[key]["datatype"]
        can_cast_rows = unchecked_values.apply(lambda x: can_cast_to(x, dtype))
        all_fails.extend(
            _get_fails(
                template_map[key],
                unchecked_values[~can_cast_rows],
                "hard",
                f"cannot_cast_to_{dtype.__name__}",
            )
        )
        unchecked_values = unchecked_values[can_cast_rows]

        cast_col = unchecked_values.astype(dtype)

        # the pipe only accepts the values in the enum despite being free text input
        # therefore we upper to avoid not in dropdown fails from case issues
        if key in [
            MetaMapper.VARS_variable_data_type.value,
            MetaMapper.VARS_key_data_type.value,
            MetaMapper.VARS_value_data_type.value,
        ]:
            cast_col = cast_col.str.upper()

        if template_map[key]["enum"]:
            all_fails.extend(
                _get_fails(
                    template_map[key],
                    cast_col[~cast_col.isin(template_map[key]["enum"])],
                    "hard",
                    "not_in_dropdown",
                )
            )
            # no extra validation if items aren't in the dropdown
            continue

        for fail_type in fail_types:
            funcs = validation_map[key].get(fail_type, [])
            for func in funcs:
                all_fails.extend(
                    _get_fails(
                        template_map[key],
                        cast_col[~cast_col.apply(func).values],
                        fail_type if key not in NON_BREAKING_MANDATORY else "soft",
                        func.__name__,
                    )
                )
    return pd.DataFrame([attrs.asdict(f) for f in all_fails])


def validate_rowwise_comparative_checks(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    rowwise_checks: List[Tuple[str, List[str], Callable, str, Dict]],
) -> pd.DataFrame:
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    all_comparative_fails = []

    for sheet, cols, func, fail_type, kwargs in tqdm(
        rowwise_checks, "validating rowwise values"
    ):
        series = xl[sheet][cols]

        if len(series) == 0:
            continue

        series_fails = ~series.apply(lambda x: func(x, **kwargs), axis=1)

        all_comparative_fails.extend(
            _get_fails(
                template_map[cols[-1]],
                series[series_fails][cols[-1]],
                fail_type,
                func.__name__,
            )
        )
    return pd.DataFrame([attrs.asdict(f) for f in all_comparative_fails])


def validate_comparative_checks(
    xl: Dict[str, pd.DataFrame],
    template_map: Dict,
    comparative_checks: List[Tuple[List[str], Callable, str, Dict]],
) -> pd.DataFrame:
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    all_comparative_fails = []

    for keys, func, fail_type, kwargs in tqdm(
        comparative_checks, "validating comparative values"
    ):
        all_comparative_fails.extend(func(xl, template_map, keys, fail_type, **kwargs))
    return pd.DataFrame([attrs.asdict(f) for f in all_comparative_fails])


def _get_excel_ref(node: Dict, idx: int):
    excel_col = re.sub(r"(\d)", "", node["value_cell"])
    if node["tab"] in [
        SheetMapper.BACK_OFFICE.value,
        SheetMapper.RESOURCE.value,
    ]:
        return node["value_cell"]
    return excel_col + str(idx + 1)


def _get_fails(
    node: Dict, indexed_series: pd.Series, fail_type: str, reason: str
) -> List[Fail]:
    return [
        Fail(
            fail_type,
            node["tab"],
            node["name"],
            value,
            reason,
            _get_excel_ref(node, idx),
        )
        for idx, value in indexed_series.to_dict().items()
    ]
