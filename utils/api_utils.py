import json, requests
from utils.format_utils import print_red
from utils.parse_utils import is_vaild_firmware_version
from utils.prompt_utils import get_credentials

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
        if input('Do you want to try again? (Y or N): ').lower() == 'y':
            get_firmware_version(config = config, print_result = print_result)

def interact_with_imd(
    config, 
    api_endpoint, 
    json_payload, 
    username, 
    password, 
    action: str = 'post', 
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
            case 'post':
                request = requests.post(endpoint, headers = headers, json = json_payload)
            case 'get':
                request = requests.get(endpoint, headers = headers)
        response = json.loads(request.text)
        if not quiet: print(response)
        if response['retCode'] == 0:
            if not quiet: print(success_msg)
            return response
    except Exception as error:
        if not quiet: print(f'Function ${function_name}: {error}')
        return False


def set_imd_creds(config, quiet = True):
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

def login_to_imd(config, quiet = True):
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

def reset_imd_to_factory_defaults(config, quiet = True):
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
    