import json, os, shutil, sys

from argparse import Namespace

from utils.dict_utils import get_value_if_key_exists
from utils.encryption_utils import encrypt
from utils.format_utils import format_red, format_blue, format_bold
from utils.parse_utils import parse_firmware_url, verify_input, is_exactly_zero, is_exactly_one, contains_unspecified_defaults
from utils.prompt_utils import confirm, enumerate_options, get_input
from utils.sys_utils import exit_with_code

def get_encyrption_passphrase(config: dict, prompts_filename: str) -> str:
    print(f'Encrypted defaults found in {format_blue(prompts_filename)}. Please set a passphrase for encrypting and decrypting these values.')
    passphrase: str = get_input(
        config = config, 
        input_type = 'getpass', 
        formatted_prompt_text = f'Please enter the encryption passphrase')
    config['passphrase'] = passphrase
    return passphrase

def get_prompt_with_default(config: dict, prompt: dict, encryption_passphrase = '', salt = b'', simulated_user_input: str = '') -> dict:
    unique_value: bool | int = get_value_if_key_exists(prompt, 'unique_value')

    if not is_exactly_zero(unique_value):
        return prompt

    prompt_input_type: str = get_value_if_key_exists(prompt, 'input_mode')
    input_type: str = prompt_input_type if bool(prompt_input_type) else 'input'
    encrypt_default = bool(get_value_if_key_exists(prompt, 'encrypt_default'))
    config_item = get_value_if_key_exists(prompt, 'prompt_text')
    prompt_text = f'Please enter the default {config_item}' if prompt_input_type == 'getpass' else f'Please enter the default {config_item}: ' 
    
    user_response = get_input(config, input_type, prompt_text, default_value = '', simulated_user_input = simulated_user_input)
    verify_function_exists = bool(get_value_if_key_exists(prompt, 'verify_function'))
    user_reponse_is_valid = bool(verify_input(config, prompt, user_response)) if verify_function_exists else True

    if not user_reponse_is_valid:
        print(format_red(f'Invalid value for \'{config_item}\', please try again.'))
        return get_prompt_with_default(config, prompt, encryption_passphrase, salt, simulated_user_input)

    if encrypt_default:
        encryption_salt, encrypted_text = encrypt(config, encryption_passphrase, user_response)
        prompt_salt = salt if bool(salt) else encryption_salt
        prompt_with_default: dict = { **prompt, "salt": prompt_salt, "default_value": encrypted_text }
    else:
        prompt_with_default = { **prompt, "default_value": user_response }

    return prompt_with_default

def get_prompts_with_defaults(config: dict, prompts_filename: str, prompts_file_path: str) -> list[dict]:
    with open(prompts_file_path, 'r') as prompts_file:
        prompts_file_contents: dict = json.load(prompts_file)
    prompts: list[dict] = prompts_file_contents['prompts']
    encrypted_defaults: list[int] = [ get_value_if_key_exists(prompt, 'encrypt_default') for prompt in prompts ]
    passphrase: str = get_encyrption_passphrase(config, prompts_filename) if 1 in encrypted_defaults else ''
    prompts_with_defaults: list[dict] = [
        get_prompt_with_default(config = config, prompt = prompt, encryption_passphrase = passphrase)
        for prompt in prompts ]

    return prompts_with_defaults

def update_prompts_file_with_defaults(config: dict) -> None:
    config_files_path: str = get_value_if_key_exists(config, 'config_files_path')
    prompts_filename: str = get_value_if_key_exists(config, 'interactive_prompts_filename')
    if bool(prompts_filename):   
        prompts_file_path: str = os.path.join(config_files_path, prompts_filename)
        with open(prompts_file_path, 'r') as prompts_file:
            prompts_file_contents = json.load(prompts_file)
            all_defaults_specified: bool = not(contains_unspecified_defaults(prompts_file_contents['prompts']))
            if all_defaults_specified:
                return
            if confirm(config, f'Do you want to set defaults for \'{format_blue(prompts_filename)}\'? '):    
                prompts_with_defaults: list[dict] = get_prompts_with_defaults(config, prompts_filename, prompts_file_path)
                updated_prompt_file_contents: dict = { **prompts_file_contents, "prompts": prompts_with_defaults}      
                with open(prompts_file_path, 'w') as prompts_file:
                    json.dump(updated_prompt_file_contents, prompts_file, indent = 4)
                print(f'Defaults written to \'{format_blue(prompts_filename)}\'!\n')

def get_config_filenames(file_type: str, config_files_path: str) -> list[str]:
    config_filenames: list[str] = [ filename for filename in os.listdir(config_files_path)
        if file_type in filename
        and '.json' in filename 
        and 'default' not in filename ]
    return config_filenames

def get_filename(file_type:str, config_files_path: str, quiet = False) -> str | bool | None:
    default_config_filename: str = f'default_{file_type}.json'
    custom_config_filename: str = f'{file_type}.json'
    default_config_file_path: str = os.path.join(config_files_path, default_config_filename)
    custom_config_file_path: str = os.path.join(config_files_path, custom_config_filename)
    config_filenames: list[str] = get_config_filenames(file_type, config_files_path)
    number_of_configs: int = len(config_filenames)

    if bool(config_filenames):
        if number_of_configs == 1:
            if not quiet:
                print(f'One {file_type} file found: \'{format_blue(config_filenames[0])}\'')
            config_filename:str | bool | None = config_filenames[0]
        if number_of_configs > 1:
            prompt: str = f'Please select a {file_type} file to load:'
            config_filename = enumerate_options(config = {}, options = config_filenames, prompt = prompt)
    else:
        prompt = f'No {file_type} files found. Do you want to make a copy of the default {file_type} file \'{format_blue(default_config_filename)}\'? (\'y\' or \'n\'): '
        if confirm(config = {}, confirm_prompt = prompt):
            shutil.copyfile(default_config_file_path, custom_config_file_path)
            if not quiet:
                print(f'Copied \'{format_blue(default_config_filename)}\' to \'{format_blue(custom_config_filename)}\'.')
            config_filename = custom_config_filename
        else:
            config_filename = None

    return config_filename

def get_config(main_file: str, args: Namespace, quiet: bool = True) -> dict:
    script_path: str = os.path.dirname(main_file)
    config_files_path: str = os.path.join(script_path, 'config')
    config_filenames: list = get_config_filenames('config', config_files_path)
    prompts_filenames: list = get_config_filenames('prompts', config_files_path)
    is_first_run: bool = not bool(config_filenames) and not bool(prompts_filenames)
    if is_first_run and not quiet:
        print(format_bold('\nWelcome to the Vertiv Geist IMD Configuration Script!\n'))
    config_filename: str = args.config_file if bool(args.config_file) else get_filename('config', config_files_path = config_files_path, quiet = quiet)
    prompts_filename: str = args.prompts_file if bool (args.prompts_file) else get_filename('prompts', config_files_path = config_files_path, quiet = quiet)
    if bool(config_filename):
        json_file_path: str = os.path.join(config_files_path, config_filename)
    else:
        print(format_red('Unable to load config file! Exiting script.'))
        exit_with_code(1)

    with open(json_file_path) as config_file:
        config: dict = json.load(config_file)
        
        imd_ip: str | None = args.imd_ip_address
        current_imd_ip: str | None = config['default_imd_ip'] if imd_ip == None else imd_ip
        parsed_firmware_url: dict | bool = parse_firmware_url(config, config['firmware_file_url'])

        finished_config = {**config, 
            "current_imd_ip": current_imd_ip,
            "api_base_url": f'https://{current_imd_ip}/api/',
            "parsed_firmware_url": parsed_firmware_url,
            "interactive_prompts_filename": prompts_filename,
            "config_files_path": config_files_path,
            "display_greeting": 0 if is_first_run else 1
            }

        return finished_config
    
