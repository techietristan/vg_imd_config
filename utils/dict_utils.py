from typing import Any

def get_dict_with_matching_key_value_pair(dicts: list[dict], key: str, value: Any) -> dict:
    for current_dict in dicts:
        if key in current_dict.keys():
            if current_dict[key] == value:
                return current_dict
    return {}


def get_value_if_key_exists(input_dict: dict, key: str):
    if key in input_dict.keys():
        return input_dict[key]
    else:
        return False
