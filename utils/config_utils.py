import json, os, shutil, sys

from utils.format_utils import format_red
from utils.parse_utils import parse_firmware_url
from utils.prompt_utils import confirm, enumerate_options, get_input

def get_filename(file_type:str, config_files_path: str, quiet = False) -> str | bool:
    default_config_filename: str = f'default_{file_type}.json'
    custom_config_filename: str = f'{file_type}.json'
    default_config_file_path: str = os.path.join(config_files_path, default_config_filename)
    custom_config_file_path: str = os.path.join(config_files_path, custom_config_filename)
    config_filenames: list = [ filename for filename in os.listdir(config_files_path)
        if file_type in filename
        and 'default' not in filename 
        and '.json' in filename ]
    number_of_configs: int = len(config_filenames)
    if bool(config_filenames):
        if number_of_configs == 1:
            if not quiet:
                print(f'One {file_type} file found: {config_filenames[0]}')
            config_filename:str = config_filenames[0]
        if number_of_configs > 1:
            prompt = f'Please select a {file_type} file to load:'
            config_filename: str = enumerate_options(config = {}, options = config_filenames, prompt = prompt)
    else:
        prompt: str = f'No {file_type} files found. Do you want to make a copy of the default {file_type} file? '
        if confirm(config = {}, confirm_prompt = prompt):
            shutil.copyfile(default_config_file_path, custom_config_file_path)
            if not quiet:
                print(f'Copied {default_config_filename} to {custom_config_filename}.')
            config_filename = custom_config_filename
        else:
            config_filename = False

    return config_filename

def get_config(main_file: str, args: list, quiet = True) -> dict:
    script_path: str = os.path.dirname(main_file)
    config_files_path: str = os.path.join(script_path, 'config')
    config_filename: str = args.config_file if bool(args.config_file) else get_filename('config', config_files_path = config_files_path, quiet = quiet)
    prompts_filename: str = args.prompts_file if bool (args.prompts_file) else get_filename('prompts', config_files_path = config_files_path, quiet = quiet)
    if bool(config_filename):
        json_file_path: str = os.path.join(config_files_path, config_filename)
    else:
        print(format_red('Unable to load config file! Exiting script.'))
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

    with open(json_file_path) as config_file:
        config: dict = json.load(config_file)
        
        imd_ip: str | None = args.imd_ip_address
        current_imd_ip: str | None = config['default_imd_ip'] if imd_ip == None else imd_ip
        parsed_firmware_url: dict = parse_firmware_url(config, config['firmware_file_url'])

        finished_config = {**config, 
            "current_imd_ip": current_imd_ip,
            "api_base_url": f'https://{current_imd_ip}/api/',
            "parsed_firmware_url": parsed_firmware_url,
            "interactive_prompts_file": prompts_filename
            }

        return finished_config

def get_prompt_default(config: dict, prompt: dict, input: str = '') -> dict:
    pass

def get_prompt_defaults(config: dict, promts_filename: str) -> None:

    if confirm(f'Do you want to set defaults for {promts_filename}? '):
        prompts_object: dict = json.load(promts_filename)
        prompts: list = prompts_object['prompts']
        


def get_input_delete_me(config: dict, input_type: str = 'input', formatted_prompt_text: str = '', default_value: str = '', simulated_user_input: str | bool = None):
    match input_type:
        case 'input':
            user_input = input(formatted_prompt_text)      
        case 'getpass':
            user_input = get_password(config = config, quiet = False)
        case 'none':
            user_input = simulated_user_input
    if user_input.strip() == '' and bool(default_value):
        return default_value
    return user_input

