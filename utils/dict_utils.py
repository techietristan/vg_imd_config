def get_value_if_key_exists(input_dict: dict, key: str):
    if key in input_dict.keys():
        return input_dict[key]
    else:
        return False