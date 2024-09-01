import json, os

def get_config(main_file, args):
    config_filename = 'default.json'
    script_path = os.path.dirname(main_file)
    json_file_path = f'{script_path}/config/{config_filename}'

    with open(json_file_path) as json_file:
        config = json.load(json_file)
    
    imd_ip = args.imd_ip_address
    current_imd_ip = config['default_imd_ip'] if imd_ip == None else imd_ip

    finished_config = {**config, 
        "current_imd_ip": current_imd_ip,
        "api_base_url": f'http://{current_imd_ip}/api/'
        }

    return finished_config
    