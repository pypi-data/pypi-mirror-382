import re

# short, permissive url regex courtesy of gskinner at https://regexr.com/3e6m0
# Update 20/9/24: Sharepoint URLs can contain parentheses after the domain
URL_PATTERN = r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=\(\)]*)"


def _regex_search(pattern: str, item: str) -> bool:
    return bool(re.search(pattern, item))


def _regex_match(pattern: str, item: str) -> bool:
    return bool(re.match(pattern, item))
