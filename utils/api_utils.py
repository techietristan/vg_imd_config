import json, requests, sys, time
from halo import Halo

from utils.firmware_utils import get_firmware_file_path
from utils.format_utils import print_red
from utils.parse_utils import is_vaild_firmware_version
from utils.prompt_utils import confirm, get_credentials

@Halo(text = 'Checking current IMD firmware version...\n', spinner = 'dots')
def get_firmware_version(config: dict, print_result: bool = False) -> str:
    api_url: str = config['api_base_url']
    api_firmware_url: str= f'{api_url}sys/version'
    headers: dict = config['headers']

    try:
        firmware_response: dict = requests.get(api_firmware_url, headers).json()
        response_code: int = firmware_response['retCode']
        firmware_version: str = firmware_response['data']
        if response_code == 0 and is_vaild_firmware_version(config = config, firmware_version = firmware_version):
            if print_result:
                time.sleep(1)
                print(f'\nCurrent IMD Firmware Version: {firmware_version}')
            return firmware_version
        else:
            print_red(firmware_response)
            raise Exception(firmware_response)
    except Exception as error:
        print_red(f'Unable to get IMD firmware version: {error}\nPlease ensure you are able to ping the IMD.')
        if confirm(confirm_prompt = 'Do you want to try again?: '):
            return get_firmware_version(config = config, print_result = print_result)

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
    success_msg: str = '') -> dict | bool:

    headers = config['headers']
    api_base_url = config['api_base_url']
    url = f'{api_base_url}{api_endpoint}'

    @Halo(text = f'{status_msg}\n', spinner = 'dots')
    def make_api_call(config):
        try:
            if not quiet: print(status_msg)
            match action:
                case 'get':
                    request = requests.get(url, headers = headers)
                case 'post':
                    request = requests.post(url, headers = headers, json = json_payload)
            response = json.loads(request.text)
            if not quiet: print(response)
            if response['retCode'] == 0:
                if not quiet: print(success_msg)
            else:
                print_red(f'IMD Error: {response}.')
            return response
        except Exception as error:
            if not quiet: print_red(f'Function \'{function_name}\' error: \'{error}\'')
            raise Exception
            return False
    return make_api_call(config)

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

def login_to_imd(config: dict, quiet: bool = True) -> dict | bool:
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
    
    return response['data']['token']

def reset_imd_to_factory_defaults(config: dict, quiet: bool = True) -> dict | bool:
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

def upgrade_imd_firmware(config: dict, quiet: bool = True) -> dict | bool:
    current_firmware_version = get_firmware_version(config, print_result = False)
    target_firmware_version = config['firmware_target']
    if current_firmware_version == target_firmware_version:
        print(f'IMD firmware already up to date (v.{current_firmware_version}).')
        return
    elif confirm(f'Current IMD firmware version is {current_firmware_version}.\nUpgrade to {target_firmware_version}? (y or n): '):
        firmware_file_path, firmware_filename = get_firmware_file_path(config = config)
        if bool(firmware_file_path):
            username, password = get_credentials(config)
            token = login_to_imd(config)
            firmware_upgrade_api_endpoint: str = f'http://{config['current_imd_ip']}/transfer/firmware?token={token}'
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
                        print_red(f'IMD Error: {response}.')
                    return response
                except Exception as error:
                    print_red(f'\nError upgrading IMD firmware: {error}')
                    if confirm('Do you want to try again (y or n): '):
                        upgrade_firmware(config)

            return upgrade_firmware(config)
        else:
            print_red('Unable to find or download firmware. Please check your configuration.')