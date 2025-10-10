import logging
from copy import deepcopy
from typing import Dict, List, Tuple

import pandas as pd
from tqdm import tqdm

import ons_metadata_validation.fixing.string_fixes as sf

logger = logging.getLogger()


FIX_FUNCTIONS = {
    "must_not_start_with_whitespace": sf.remove_whitespace,
    "must_not_end_with_whitespace": sf.remove_whitespace,
    "must_end_with_a_full_stop_or_question_mark": sf.add_full_stop,
    "must_not_contain_double_spaces": sf.remove_multiple_spaces,
    "must_be_alphanumeric_only": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_spaces": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_underscores": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_spaces_or_underscores": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_dashes": sf.replace_non_breaking_space,
    "must_have_leading_apostrophe": sf.add_leading_apostrophe,
    "must_start_with_capital": sf.add_capital_at_start,
    "must_have_caps_after_commas": sf.add_capitals_after_commas,
    "must_not_say_ONS": sf.convert_to_ONS,
}


def apply_fixes(
    xl: Dict[str, pd.DataFrame],
    validation_map: dict,
    fail_types: List[str] = ["hard", "soft"],
) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """Apply fixes to the xl.

    Args:
        xl (Dict[str, pd.DataFrame]): The xl.
        validation_map (dict): The single value validations.
        fail_types (List[str], optional): The types of fails to correct. Defaults to ["hard", "soft"].

    Returns:
        Tuple[Dict[str, pd.DataFrame], pd.DataFrame]: The corrected xl and the dataframe listing the fixes applied
    """

    applied_fixes = []
    xl = deepcopy(xl)

    for tab in tqdm(xl, "Applying fixes"):
        for col in xl[tab].columns:
            if col not in validation_map:
                continue
            for fail_type in fail_types:
                for func in validation_map[col].get(fail_type, []):
                    if func.__name__ not in FIX_FUNCTIONS:
                        continue
                    xl[tab][col] = xl[tab][col].apply(FIX_FUNCTIONS[func.__name__])
                    applied_fixes.append(
                        {
                            "tab": tab,
                            "name": col,
                            "fail_type": fail_type,
                            "attempted_fix": func.__name__,
                        }
                    )
    return xl, pd.DataFrame(applied_fixes)
