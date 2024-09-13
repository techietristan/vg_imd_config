import json, requests, sys
from utils.format_utils import print_red
from utils.parse_utils import is_vaild_firmware_version
from utils.prompt_utils import confirm, get_credentials

def get_firmware_version(config: dict, print_result: bool = False) -> str:
    api_url: str = config['api_base_url']
    api_firmware_url: str= f'{api_url}sys/version'
    headers: dict = config['headers']

    try:
        firmware_response: dict = requests.get(api_firmware_url, headers).json()
        response_code: int = firmware_response['retCode']
        firmware_version: str = firmware_response['data']
        if response_code == 0 and is_vaild_firmware_version(firmware_version):
            if print_result:
                print(f'Current IMD Firmware Version: {firmware_version}')
            return firmware_version
        else:
            raise Exception(firmware_response)
    except:
        print_red('Unable to get IMD firmware version.\nPlease ensure you are able to ping the IMD.')
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
    endpoint = f'{api_base_url}{api_endpoint}'

    try:
        if not quiet: print(status_msg)
        match action:
            case 'get':
                request = requests.get(endpoint, headers = headers)
            case 'post':
                request = requests.post(endpoint, headers = headers, json = json_payload)
            case 'upload':
                request = requests.post(endpoint, headers = headers, files = upload_file, verify = False)
        response = json.loads(request.text)
        if not quiet: print(response)
        if response['retCode'] == 0:
            if not quiet: print(success_msg)
            return response
    except Exception as error:
        if not quiet: print_red(f'Function \'{function_name}\' error: \'{error}\'')
        raise Exception
        return False

def set_imd_creds(config: dict, quiet: bool = True):
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

def login_to_imd(config: dict, quiet: bool = True):
    username, password = get_credentials(config)
    creds_api_endpoint: str = f'auth/{username}'
    login_json: dict = {'token': '', 'cmd': 'login', 'data': {'password': password}}

    interact_with_imd(
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

def reset_imd_to_factory_defaults(config: dict, quiet: bool = True):
    username, password = get_credentials(config)
    creds_api_endpoint: str = f'sys/'
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

def upgrade_imd_firmware(config: dict, firmware_file_path: str, firmware_filename: str, quiet: bool = True):
    username, password = get_credentials(config)
    firmware_upgrade_api_endpoint: str = f'transfer/firmware?username={username}?password={password}'

    interact_with_imd(
        config = config, 
        api_endpoint = firmware_upgrade_api_endpoint,
        json_payload = {},
        username = username,
        password = password, 
        action = 'upload', 
        upload_file = {'file': (firmware_filename, open(firmware_file_path, 'rb'))},
        quiet = quiet, 
        function_name = 'upgrade_imd_firmware', 
        status_msg = 'Upgrading IMD Firmware.',
        success_msg = 'Successfully Upgraded IMD Firmware!')
