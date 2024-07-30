from collections import namedtuple
from typing import Dict, Optional


def match(data: Dict, pattern: Dict) -> Optional[namedtuple]:  # noqa PYI024
    """
    Check if a dictionary (`data`) matches a specified pattern (`pattern`).

    This function verifies if the structure and types of `data` conform to those
    defined in `pattern`. If they match, a named tuple containing the matching values
    is returned. If not, the function returns `None`.

    :param data: The dictionary to be checked against the pattern.
    :param pattern: The dictionary defining the structure and expected types for matching.
    :return: A named tuple with the matching values if `data` matches `pattern`. `None` if there is no match.
    :raise ValueError: If a type is used as a key in the `pattern` dictionary.
    """
    if not (isinstance(data, dict) or isinstance(pattern, dict)):
        return None

    if len(data) != len(pattern):
        return None

    result_data: Dict = {}
    for pattern_key, pattern_value in pattern.items():
        if isinstance(pattern_key, type):
            message: str = f"Can't use types as pattern keys: {pattern}. Key: {pattern_key}."
            raise ValueError(message)

        if pattern_key not in data:
            return None

        value = data[pattern_key]
        if isinstance(pattern_value, type) and isinstance(value, pattern_value):
            result_data[pattern_key] = value
        elif isinstance(pattern_value, dict) and (mr := match(value, pattern_value)):
            result_data[pattern_key] = mr
        elif pattern_value == value:
            result_data[pattern_key] = value
        else:
            return None

    return namedtuple(typename="MatchResult", field_names=result_data.keys())(*result_data.values())  # noqa PYI024
