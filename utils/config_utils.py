import json, os

from utils.parse_utils import parse_firmware_url

def get_config(main_file: str, args: list):
    config_filename: str = 'default.json'
    script_path: str = os.path.dirname(main_file)
    json_file_path: str = f'{script_path}/config/{config_filename}'

    with open(json_file_path) as json_file:
        config: dict = json.load(json_file)
    
    imd_ip: str | None = args.imd_ip_address
    current_imd_ip: str | None = config['default_imd_ip'] if imd_ip == None else imd_ip
    parsed_firmware_url: dict = parse_firmware_url(config, config['firmware_file_url'])

    finished_config = {**config, 
        "current_imd_ip": current_imd_ip,
        "api_base_url": f'http://{current_imd_ip}/api/',
        "parsed_firmware_url": parsed_firmware_url
        }

    return finished_config