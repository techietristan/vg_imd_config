import json, os, shutil, sys

from argparse import Namespace

from utils.dict_utils import get_value_if_key_exists, get_values_if_keys_exist
from utils.encryption_utils import encrypt, decrypt
from utils.format_utils import format_red, format_blue, format_bold
from utils.parse_utils import parse_firmware_url, verify_input, contains_unspecified_defaults
from utils.prompt_utils import confirm, enumerate_options, get_input
from utils.sys_utils import exit_with_code
from utils.time_utils import get_file_modification_time

spinners: list[str] = ['dots', 'dots2', 'dots3', 'dots4', 'dots5', 'dots6', 'dots7', 'dots8', 'dots9', 'dots10', 'dots11', 'dots12', 'line', 'line2', 'pipe', 'simpleDots', 'simpleDotsScrolling', 'star', 'star2', 'flip', 'hamburger', 'growVertical', 'growHorizontal', 'balloon', 'balloon2', 'noise', 'bounce', 'boxBounce', 'boxBounce2', 'triangle', 'arc', 'circle', 'squareCorners', 'circleQuarters', 'circleHalves', 'squish', 'toggle', 'toggle2', 'toggle3', 'toggle4', 'toggle5', 'toggle6', 'toggle7', 'toggle8', 'toggle9', 'toggle10', 'toggle11', 'toggle12', 'toggle13', 'arrow', 'arrow2', 'arrow3', 'bouncingBar', 'bouncingBall', 'smiley', 'monkey', 'hearts', 'clock', 'earth', 'moon', 'runner', 'pong', 'shark', 'dqpb']

def get_encyrption_passphrase(config: dict, prompts_filename: str) -> str:
    print(f'Encrypted defaults found in \'{format_blue(prompts_filename)}\'. Please set a passphrase for encrypting and decrypting these values.')
    passphrase: str = get_input(
        config = config,
        input_type = 'getpass',
        formatted_prompt_text = 'Please enter the encryption passphrase')
    config['passphrase'] = passphrase
    return passphrase

def get_prompt_with_default(config: dict, prompt: dict, encryption_passphrase = '', salt: bytes = b'', simulated_user_input: str = '') -> dict:
    is_unique_value: bool = bool('unique_value' not in prompt.keys() or get_value_if_key_exists(prompt, 'unique_value'))
    if is_unique_value: return prompt

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

def get_prompts_file_contents(config: dict) -> tuple:
    config_files_path: str = get_value_if_key_exists(config, 'config_files_path')
    prompts_filename: str = get_value_if_key_exists(config, 'interactive_prompts_filename')
    if bool(config_files_path) and bool(prompts_filename):   
        prompts_file_path: str = os.path.join(config_files_path, prompts_filename)
        with open(prompts_file_path, 'r') as prompts_file:
            prompts_file_contents: dict = json.load(prompts_file)
    else:
        return (False, False, False)

    return prompts_filename, prompts_file_path, prompts_file_contents
    
def update_prompts_file_with_defaults(config: dict) -> None:
    prompts_filename, prompts_file_path, prompts_file_contents = get_prompts_file_contents(config)
    if not prompts_filename or not prompts_file_contents:
        return
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
            config_filename: str | bool | None = config_filenames[0]
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

def get_spinner(config: dict, args: Namespace) -> str:
    specified_spinner: str | None = args.spinner
    spinner: str = specified_spinner if bool(specified_spinner) and specified_spinner in spinners else config['default_spinner']
    unicode_supported: bool = bool(sys.stdout.encoding.lower().startswith('utf'))
    if not unicode_supported:
        return 'line'
    return spinner

def get_config(main_file: str, args: Namespace, quiet: bool = True) -> dict:
    script_path: str = os.path.dirname(main_file)
    config_files_path: str = os.path.join(script_path, 'config')
    config_filenames: list = get_config_filenames('config', config_files_path)
    prompts_filenames: list = get_config_filenames('prompts', config_files_path)
    is_first_run: bool = not bool(config_filenames) and not bool(prompts_filenames)
    if is_first_run and not quiet:
        print(format_bold('\nWelcome to the Vertiv Geist IMD Configuration Script!\n'))
    config_filename: str | bool | None = args.config_file if bool(args.config_file) else get_filename('config', config_files_path = config_files_path, quiet = quiet)
    prompts_filename: str | bool | None = args.prompts_file if bool (args.prompts_file) else get_filename('prompts', config_files_path = config_files_path, quiet = quiet)
    if type(config_filename) == str:
        json_file_path: str = os.path.join(config_files_path, config_filename)
    else:
        print(format_red('Unable to load config file! Exiting script.'))
        exit_with_code(1)

    with open(json_file_path) as config_file:
        initial_config: dict = json.load(config_file)
        
        imd_ip: str | None = args.imd_ip_address
        current_imd_ip: str | None = initial_config['default_imd_ip'] if imd_ip == None else imd_ip
        spinner: str = get_spinner(initial_config, args)
        parsed_firmware_url: dict | bool = parse_firmware_url(initial_config, initial_config['firmware_file_url'])

        finished_config = {**initial_config, 
            "current_imd_ip": current_imd_ip,
            "imd_base_url": f'https://{current_imd_ip}',
            "api_base_url": f'https://{current_imd_ip}/api/',
            "parsed_firmware_url": parsed_firmware_url,
            "interactive_prompts_filename": prompts_filename,
            "config_files_path": config_files_path,
            "display_greeting": False if is_first_run else True,
            "spinner": spinner,
            "api_attempts": initial_config['default_api_attempts'],
            "api_retry_time": initial_config['default_api_retry_time']
            }

        return finished_config

def get_credentials_from_imd_config(config: dict, imd_config: list[dict]) -> tuple[str, str]:
    credentials_config_item: dict = [ config_item for config_item in imd_config if config_item['config_item'] == 'credentials' ][0]
    data: dict = json.loads(credentials_config_item['api_calls'][0]['data'].replace('\'', '\"'))
    username, password = data['username'], data['password']

    return username, password
    
def write_current_imd_config_to_file(config: dict, imd_config: list[dict], quiet: bool = True) -> None:
    prompts_filename, prompts_file_path, prompts_file_contents = get_prompts_file_contents(config)
    write_temp_imd_config_file, encrypt_temp_imd_config_file, temp_imd_config_filename = get_values_if_keys_exist(prompts_file_contents, ['write_temp_imd_config_file', 'encrypt_temp_imd_config_file', 'temp_imd_config_filename'])
    config_files_path, passphrase = get_values_if_keys_exist(config, ['config_files_path', 'passphrase'])
    config_json: str = json.dumps(imd_config)
    if not bool(write_current_imd_config_to_file) or not bool(temp_imd_config_filename) or not bool(config_files_path):
        return
    imd_config_file_path: str = os.path.join(config_files_path, temp_imd_config_filename) #type: ignore[arg-type]
    encrypt_contents: bool = bool(encrypt_temp_imd_config_file) and bool(passphrase)
    if encrypt_contents:
        salt, encrypted_config_file_contents = encrypt(config, passphrase, config_json) # type: ignore[arg-type]
        imd_config_file_contents: str = f'salt: {salt}\n{encrypted_config_file_contents}'
    else:
        imd_config_file_contents = config_json

    with open(imd_config_file_path, 'w') as imd_config_file:
        if not quiet:
            print(f'Saving current IMD config to {imd_config_file_path}')
        imd_config_file.write(imd_config_file_contents)

def get_previous_imd_config(config: dict) -> list[dict] | bool:
    prompts_filename, prompts_file_path, prompts_file_contents = get_prompts_file_contents(config)
    temp_imd_config_filename: str | bool = get_value_if_key_exists(prompts_file_contents, 'temp_imd_config_filename')
    config_files_path: str = get_value_if_key_exists(config, 'config_files_path')
    imd_config_file_path: str = os.path.join(config_files_path, temp_imd_config_filename) #type: ignore[arg-type]
    passphrase: str | bool = get_value_if_key_exists(config, 'passphrase')
    if os.path.isfile(imd_config_file_path):
        modified_on: str = get_file_modification_time(imd_config_file_path, '%Y-%m-%d')
        modified_at: str = get_file_modification_time(imd_config_file_path, '%H:%M:%S')
        print(f'Unfinished IMD configuration found: \'{format_blue(temp_imd_config_filename)}\', modified on {format_blue(modified_on)} at {format_blue(modified_at)}.') #type: ignore[arg-type]
        if confirm(config, 'Load this configuration? (y or n): ') and bool(passphrase):
            with open(imd_config_file_path) as imd_config_file:
                imd_config_file_contents: list = imd_config_file.read().splitlines()
                if 'salt: ' in imd_config_file_contents[0]:
                    salt: str = imd_config_file_contents[0].split(' ')[1]
                    previous_imd_config: str = decrypt(config, salt, imd_config_file_contents[1], passphrase) #type: ignore[assignment, arg-type]
                    parsed_previous_imd_config: list[dict] = json.loads(previous_imd_config)

                else:
                    parsed_previous_imd_config = json.loads(imd_config_file_contents[0])
                config['username'], config['password'] = get_credentials_from_imd_config(config, parsed_previous_imd_config)

                return parsed_previous_imd_config
                
        elif confirm(config, 'Delete this configuration? (y or n): '):
            os.remove(imd_config_file_path)
            return False

    return False

def remove_previous_imd_config(config: dict) -> None:
    prompts_filename, prompts_file_path, prompts_file_contents = get_prompts_file_contents(config)
    temp_imd_config_filename: str | bool = get_value_if_key_exists(prompts_file_contents, 'temp_imd_config_filename')
    config_files_path: str = get_value_if_key_exists(config, 'config_files_path')
    imd_config_file_path: str = os.path.join(config_files_path, temp_imd_config_filename) #type: ignore[arg-type]

    if os.path.isfile(imd_config_file_path): os.remove(imd_config_file_path)
    