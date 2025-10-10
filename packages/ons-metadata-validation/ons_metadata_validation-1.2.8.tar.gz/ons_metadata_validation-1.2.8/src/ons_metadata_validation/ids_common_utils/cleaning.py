from typing import Any

import pandas as pd


def trim_whitespace(item: Any) -> Any:
    """Trim whitespace from string if not null.

    Args:
        item (Any): The item to strip.

    Returns:
        str | Any: Null or the item.
    """
    if pd.notna(item):
        return str(item).strip()
    return item


def trim_whitespace_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Trim all rows that are just whitespace or empty strings.

    Args:
        df (pd.DataFrame): The input df.

    Returns:
        pd.DataFrame: The modified df.
    """
    return df[~df.applymap(trim_whitespace).eq("").all(axis=1)]
