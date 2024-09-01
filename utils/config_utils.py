import json, os

def get_config(main_file):
    config_filename = 'default.json'
    script_path = os.path.dirname(main_file)
    json_file_path = f'{script_path}/config/{config_filename}'

    with open(json_file_path) as json_file:
        config_dict = json.load(json_file)
        return config_dict


    