import re
from typing import Any


def remove_whitespace(item: Any) -> Any:
    """strips leading/trailing whitespace from string

    Args:
        item (str): item with whitespace

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified str without leading/trailing whitespace
    """
    if not isinstance(item, str):
        return item
    return item.strip()


def add_full_stop(item: Any) -> Any:
    """adds full stop to item. Strips the string first to avoid the following
    example where there is another whitespace character at the end of the string

    without stripping first:
    >>> "does not end with full stop. "
    >>> add_full_stop("does not end with full stop. ")
    >>> # output: "does not end with full stop. ."

    with stripping first:
    >>> "does not end with full stop. "
    >>> add_full_stop("does not end with full stop. ")
    >>> # output: "does not end with full stop."

    Args:
        item (str): item without a full stop at the end

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified item with full stop at the end
    """
    if not isinstance(item, str):
        return item

    item = item.strip()

    if item:
        if item[-1] in ["?", ".", "!"]:
            return item
        return item + "."
    return item


def remove_multiple_spaces(item: Any) -> Any:
    """remove double, triple, n+ spaces and replace with single space

    Args:
        item (str): item with double+ spaces

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified item with only single spaces
    """
    if not isinstance(item, str):
        return item
    return re.sub(r" +", r" ", item)


def replace_non_breaking_space(item: Any) -> Any:
    """replaces the non ascii character '\\xa0' with a single space.
    May add more chars as more are found.

    Args:
        item (str): item with '\\xa0'

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified item with only single spaces
    """
    if not isinstance(item, str):
        return item
    return item.replace("\xa0", " ").strip()


def add_leading_apostrophe(item: Any) -> Any:
    """Add leading apostrophe to item if str.

    Args:
        item (Any): the item.

    Returns:
        Any: The item if not a str or the item with a leading apostrophe.
    """
    if not isinstance(item, str) or item.startswith("'"):
        return item
    return f"'{item}"


def add_capital_at_start(item: Any) -> Any:
    """Capitalise first character to item if str.

    Args:
        item (Any): the item.

    Returns:
        Any: The item if not a str or the item starting with a capital.
    """
    # account for empty strings
    if not isinstance(item, str) or not item:
        return item
    return item[0].upper() + item[1:]


def add_capitals_after_commas(item: Any) -> Any:
    if not isinstance(item, str) or not item:
        return item
    items = item.split(",")
    items = [add_capital_at_start(item.strip()) for item in items]
    return ", ".join(items)


def convert_to_ONS(item: Any) -> Any:
    if not isinstance(item, str) or not item:
        return item

    if remove_multiple_spaces(item.lower().strip()) in [
        "ons",
        "office of national statistics",
        "office for national statistics",
    ]:
        return "Office for National Statistics"
    return item
