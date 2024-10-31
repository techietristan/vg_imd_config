import json, requests, sys, time, urllib3
from halo import Halo # type: ignore
from requests import Response
from typing import Callable

from utils.dict_utils import get_dict_with_matching_key_value_pair, get_value_if_key_exists
from utils.firmware_utils import get_firmware_file_path
from utils.format_utils import format_green, format_blue, format_red, get_formatted_config_items
from utils.parse_utils import is_vaild_firmware_version
from utils.prompt_utils import confirm, get_credentials

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_firmware_version(config: dict, quiet: bool = False) -> str | bool:
    spinner: Halo = Halo(text = 'Checking current IMD firmware version...\n', spinner = 'dots')
    api_url: str = config['api_base_url']
    api_firmware_url: str= f'{api_url}sys/version'
    headers: dict = config['headers']
    try:
        spinner.start()
        firmware_response: dict = requests.get(api_firmware_url, headers = headers, verify = False).json()
        response_code: int = firmware_response['retCode']
        firmware_version: str = firmware_response['data']
        if response_code == 0 and is_vaild_firmware_version(config = config, firmware_version = firmware_version):
            if not quiet:
                time.sleep(1)
                spinner.succeed(f'\nCurrent IMD Firmware Version: {firmware_version}')
            else:
                spinner.stop()
            return firmware_version
        else:
            spinner.fail(firmware_response)
            raise Exception(firmware_response)
    except Exception as error:
        spinner.fail(f'Unable to get IMD firmware version: {error}\nPlease ensure you are able to ping the IMD.')
        if confirm(config, confirm_prompt = 'Do you want to try again?: '):
            return get_firmware_version(config = config, quiet = quiet)
    return False

def make_api_call(
    config: dict,
    url: str, 
    headers: dict, 
    json_payload: dict, 
    action: str = 'post',
    status_msg: str = '',
    success_msg: str = '',
    function_name: str = '',
    quiet: bool = False) -> Response | bool:

    spinner = Halo(text = f'{status_msg}\n', spinner = 'dots')
    try:
        spinner.start()
        match action:
            case 'get':
                request = requests.get(url, headers = headers, verify = False)
            case 'post':
                request = requests.post(url, headers = headers, json = json_payload, verify = False)
        response = json.loads(request.text)
        if not quiet: print(response)
        if response['retCode'] == 0:
            if not quiet: spinner.succeed(success_msg)
        else:
            spinner.fail(f'IMD Error: {response['retMsg']}.')
        return response
    except requests.exceptions.ConnectionError as error:
        spinner.fail(f'Error while interacting with IMD: {error}.')
        if confirm(config, 'Do you want to try again? (y or n): '):
            make_api_call(config, url, headers, json_payload, action, status_msg, success_msg, function_name, quiet)
    except Exception as error:
        if not quiet: spinner.fail(f'Function \'{function_name}\' error: \'{error}\'')
        
    return False

def interact_with_imd(
    config: dict, 
    api_endpoint: str, 
    json_payload: dict, 
    username: str, 
    password: str, 
    action: str = 'post',
    upload_file: tuple = (),
    quiet: bool = True, 
    function_name: str = '', 
    status_msg: str = '', 
    success_msg: str = '') -> Response | bool:

    headers = config['headers']
    api_base_url = config['api_base_url']
    url = f'{api_base_url}{api_endpoint}'

    return make_api_call(config = config,
    url = url, 
    headers = headers, 
    json_payload = json_payload, 
    action = action,
    status_msg = status_msg,
    success_msg = success_msg,
    function_name = function_name,
    quiet = quiet)

def set_imd_creds(config: dict, quiet: bool = True) -> dict | bool:
    username, password = get_credentials(config)
    creds_api_endpoint: str = f'auth/'
    new_user_settings: dict = {'token': '', 'cmd': 'add', 'data': {'username': username, 'password': password, 'enabled': 'true', 'control': 'true', 'admin': 'true', 'language': 'en'}}

    interact_with_imd(
        config = config, 
        api_endpoint = creds_api_endpoint,
        json_payload = new_user_settings,
        username = username,
        password = password, 
        action = 'post', 
        quiet = quiet, 
        function_name = 'set_imd_creds', 
        status_msg = 'Setting IMD Credentials.',
        success_msg = 'Successfully Set IMD credentials!')

    return False

def login_to_imd(config: dict, quiet: bool = True) -> str | bool:
    username, password = get_credentials(config)
    login_api_endpoint: str = f'auth/{username}'
    login_json: dict = {'token': '', 'cmd': 'login', 'data': {'password': password}}

    response = interact_with_imd(
        config = config, 
        api_endpoint = login_api_endpoint,
        json_payload = login_json,
        username = username,
        password = password, 
        action = 'post', 
        quiet = quiet, 
        function_name = 'login_to_imd', 
        status_msg = 'Logging into IMD.',
        success_msg = 'Successfully Logged into IMD!')
    
    if type(response) == Response:
        return response['data']['token'] # type: ignore
    return False

def reset_imd_to_factory_defaults(config: dict, quiet: bool = True) -> dict | None:
    username, password = get_credentials(config)
    reset_api_endpoint: str = f'sys/'
    factory_reset_json: dict = {'username': username, 'password': password, 'cmd': "reset", 'data': {'target': "defaults"}}

    interact_with_imd(
        config = config, 
        api_endpoint = reset_api_endpoint,
        json_payload = factory_reset_json,
        username = username,
        password = password, 
        action = 'post', 
        quiet = quiet, 
        function_name = 'reset_imd_to_factory_defaults', 
        status_msg = 'Resetting IMD to Factory Defaults.',
        success_msg = 'Successfully Reset IMD to Factory Defaults!')
    
    return None

def upgrade_imd_firmware(config: dict, quiet: bool = True) -> dict | bool:
    current_firmware_version = get_firmware_version(config, quiet = True)
    target_firmware_version = config['firmware_target']
    if current_firmware_version == target_firmware_version:
        print(f'IMD firmware already up to date (v.{current_firmware_version}).')
        return False
    elif confirm(config, f'Current IMD firmware version is {current_firmware_version}.\nUpgrade to {target_firmware_version}? (y or n): '):
        firmware_file_path, firmware_filename = get_firmware_file_path(config = config)
        if bool(firmware_file_path):
            username, password = get_credentials(config)
            token = login_to_imd(config)
            firmware_upgrade_api_endpoint: str = f'https://{config['current_imd_ip']}/transfer/firmware?token={token}'
            firmware_upgrade_headers: dict = {'Content_Type' : 'multipart/form-data'}
            
            @Halo(text = 'Upgrading IMD Firmware...', spinner = 'dots')
            def upgrade_firmware(config):
                try:
                    request = requests.post(
                        firmware_upgrade_api_endpoint, 
                        headers = firmware_upgrade_headers, 
                        files={'firmware_file': open(firmware_file_path, 'rb')})
                    response = json.loads(request.text)
                    print(response['retMsg'])
                    if not quiet: print(response)
                    if response['retCode'] == 0:
                        if not quiet: print('Firmware upgraded successfully!')
                    else:
                        print(format_red(f'IMD Error: {response}.'))
                    return response
                except Exception as error:
                    print(format_red(f'\nError upgrading IMD firmware: {error}'))
                    if confirm('\nDo you want to try again (y or n): '):
                        upgrade_firmware(config)

            return upgrade_firmware(config)
        else:
            print(format_red('Unable to find or download firmware. Please check your configuration.'))
        
    return False

def get_ordered_api_calls(config: dict, prompts: dict, unique_config_items: list[dict]) -> list[dict]:
    api_call_sequence: list[str] = prompts['api_call_sequence']
    formatted_config_items: list[dict] = get_formatted_config_items(config, prompts, unique_config_items)
    defaults: list[dict] = prompts['defaults']
    api_calls: list[dict] = formatted_config_items + defaults
    ordered_api_calls: list[dict] = [
        get_dict_with_matching_key_value_pair(api_calls, 'config_item', api_call)
        for api_call in api_call_sequence
    ]

    return ordered_api_calls

def apply_api_calls(config: dict, api_call: dict, quiet=False) -> bool:
    config_item_name: str = get_value_if_key_exists(api_call, config_item_name)
    api_calls: list[dict] = get_value_if_key_exists(api_call, 'api_calls')
    headers = config['headers']
    for api_call in api_calls:
        method: str = get_value_if_key_exists(api_call, 'method')
        command: str = get_value_if_key_exists(api_call, 'cmd')
        data: dict = get_value_if_key_exists(api_call, 'data')
        api_path: str = get_value_if_key_exists(api_call, 'api_path')
        url = f'config[]'
        status_message: str = f'Setting {config_item_name}\n' if command == 'set' else f'Removing {config_item_name}\n' if command == 'del' else ''
        success_message: str = f'{config_item_name} set successfully!\n' if command == 'set' else f'{config_item_name} removed successfully!\n' if command == 'del' else ''
        failure_message: str = f'Failed to set {config_item_name}!\n' if command == 'set' else f'Failed to remove {config_item_name}!\n' if command == 'del' else ''

        def retry(api_call: dict) -> bool:
            if confirm(config, 'Do you want to try again? (y or n): '):
                return apply_api_calls(config, api_call, quiet)
            return False

        spinner = Halo(text = format_blue(f'{status_message}\n'), spinner = 'dots')
        try:
            if not quiet: spinner.start()
            if not bool(data) and command == 'del': request = requests.post(url, headers = headers,  verify = False)
            if bool(data) and method == 'post': request = requests.post(url, headers = headers, json = data, verify = False)
            if bool(request):
                response: dict = json.loads(request.text)
                if response['retCode'] == 0:
                    if not quiet and bool(success_message): spinner.succeed(format_green(success_message))
                    return True
                else: 
                    if not quiet and bool(failure_message): spinner.fail(format_red(f'{failure_message} | IMD Error: {response['retMsg']}.'))
                    retry(api_call)
                    return False

        except requests.exceptions.ConnectionError as error:
            spinner.fail(format_red(f'Error while interacting with IMD: {error}.'))
            retry(api_call)
        except Exception as error:
            if not quiet and bool(failure_message): spinner.fail(format_red(f'Function \'{config_item_name}\' error: \'{error}\''))
            retry(api_call)
            
    return False