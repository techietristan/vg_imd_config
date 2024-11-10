import json, requests, time, urllib3
from halo import Halo # type: ignore
from requests import Response

from utils.dict_utils import get_dict_with_matching_key_value_pair, get_values_if_keys_exist
from utils.format_utils import format_red, format_yellow, format_green, format_blue, get_formatted_config_items, get_status_messages
from utils.parse_utils import is_exactly_zero
from utils.prompt_utils import confirm, get_credentials
from utils.network_utils import wait_for_ping
from utils.sys_utils import exit_with_code

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def make_api_call(
    config: dict,
    url: str, 
    headers: dict, 
    json_payload: dict = {}, 
    action: str = 'post',
    status_msg: str = '',
    success_msg: str = '',
    function_name: str = '',
    quiet: bool = False) -> Response | bool:

    spinner = Halo(text = f'{status_msg}\n', spinner = config['spinner'])
    try:
        if not quiet: spinner.start()
        match action:
            case 'get':
                request = requests.get(url, headers = headers, verify = False)
            case 'post':
                request = requests.post(url, headers = headers, json = json_payload, verify = False)
        response = json.loads(request.text)
        response_code = response['retCode']
        if is_exactly_zero(response_code):
            if not quiet: spinner.succeed(success_msg)
        else:
            response_message: str = response['retMsg']
            failure_message: str = response_message if bool(response_message) else f'Return Code: {response_code}' if bool(response_code) else response
            if not quiet: spinner.fail(f'IMD Error: {failure_message}.')
        return response
    except requests.exceptions.ConnectionError as error:
        if not quiet: 
            spinner.fail(f'Error while interacting with IMD: {error}.')
            if not confirm(config, 'Do you want to try again? (y or n): '):
                if not confirm(config, 'Do you want to continue with the configuration? (y or n): '):
                    exit_with_code(1)
            else: make_api_call(config, url, headers, json_payload, action, status_msg, success_msg, function_name, quiet)
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
    url = f'{api_base_url}{api_endpoint}' if api_endpoint[0] != '/' else f'{config['imd_base_url']}{api_endpoint}'

    return make_api_call(config = config,
    url = url, 
    headers = headers, 
    json_payload = json_payload, 
    action = action,
    status_msg = status_msg,
    success_msg = success_msg,
    function_name = function_name,
    quiet = quiet)

def get_admin_status(config: dict) -> bool:
    admin_status: Response | bool = interact_with_imd(config, 'sys/state/adminExists', {}, '', '', 'get', quiet = True)
    if type(admin_status) != bool: admin_exists: bool = bool(admin_status['data']) #type: ignore[index]
    else: admin_exists = False
    
    return admin_exists

def set_imd_creds(config: dict, quiet: bool = True) -> Response | bool:
    username, password = get_credentials(config)
    creds_api_endpoint: str = 'auth/'
    new_user_settings: dict = {'token': '', 'cmd': 'add', 'data': {'username': username, 'password': password, 'enabled': 'true', 'control': 'true', 'admin': 'true', 'language': 'en'}}

    return interact_with_imd(
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
    admin_exists: bool = get_admin_status(config)

    if not admin_exists: set_imd_creds(config, True)
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
    
    if type(response) == dict:
        try:
            return response['data']['token'] # type: ignore
        except KeyError:
            if not confirm(config, format_red('Unable to log into IMD. Do you want to try again? (y or n): ')):
                if not quiet: print(format_red('Unable to log into IMD. Please reset the IMD to factory defaults.'))
            else: return login_to_imd(config, quiet)
    return False

def reset_imd_to_factory_defaults(config: dict, quiet: bool = True) -> Response | bool:
    if wait_for_ping(config, quiet = False):
        admin_exists: bool = get_admin_status(config)
        if not admin_exists and not quiet:
            print(format_yellow('The IMD is already set to factory defaults.'))
            return False
        username, password = get_credentials(config)
        reset_api_endpoint: str = 'sys/'
        factory_reset_json: dict = {'username': username, 'password': password, 'cmd': "reset", 'data': {'target': "defaults"}}

        return interact_with_imd(
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

def apply_api_call(config: dict, config_item_name: str, api_call: dict, retry_attempts: int, quiet=False) -> bool:
    def retry(retry_attempts: int, spinner: Halo, message: str) -> bool:
        if not quiet: spinner.fail(format_red(message))
        auto_retry: bool = retry_attempts > 0
        retry_wait_time: int = config['api_retry_time'] 
        if auto_retry:
            time.sleep(retry_wait_time)
            if not quiet: print("\033[A\033[A")
            return apply_api_call(config, config_item_name, api_call, retry_attempts - 1, quiet) 
        if not confirm(config, 'Do you want to try again? (y or n): '):
            if not confirm(config, 'Do you want to continue with the configuration? (y or n): '): 
                if not quiet: print(format_yellow('Exiting the script. You may wish to reset the IMD to factory defaults.'))
                exit_with_code(1)
            return False
        return apply_api_call(config, config_item_name, api_call, config['api_attempts'], quiet)

    method, command, raw_data, api_path = get_values_if_keys_exist(api_call, ['method', 'cmd', 'data', 'api_path'])
    if bool(raw_data):
        data: dict = raw_data if type(raw_data) == dict else json.loads(raw_data.replace('\'', '\"'))
    api_attempts, default_api_retry_time, headers = get_values_if_keys_exist(config, ['default_api_attempts', 'default_api_retry_time', 'headers'])
    url = f'{config['api_base_url']}{api_path}' if api_path[0] != '/' else f'{config['imd_base_url']}{api_path}'
    status_message, success_message, failure_message = get_status_messages(config, config_item_name, command)
    spinner = Halo(spinner = config['spinner'])
    if not quiet: spinner.start(text = status_message)
    try:
        wait_for_ping(config, quiet = True)
        if bool(raw_data) and method == 'post': 
            if command == 'add': json_data: dict = {'token': '', 'cmd': 'add', 'data': data}
            elif command == 'set': json_data = {'username': config['username'], 'password': config['password'], 'cmd': 'set', 'data': data}
            request = requests.post(url, headers = headers, json = json_data, verify = False)
        if not bool(raw_data) and command == 'delete':   
            request = requests.post(url, headers = headers, json = {'username': config['username'], 'password': config['password'], 'cmd': 'delete'}, verify = False)
        if bool(request):
            response: dict = json.loads(request.text)
            api_response_message, api_response_code = response['retMsg'], response['retCode']
            api_call_successful: bool = bool(api_response_code == 0)
            credentials_already_set: bool = api_path == 'auth' and api_response_message == 'Not enough permissions'
            config_item_already_deleted: bool = api_response_code == 3001 and command == 'delete'
            
            if api_call_successful or credentials_already_set or config_item_already_deleted:
                if not quiet and bool(success_message): spinner.succeed(text = success_message)
                return True
            if api_response_code == 1001:
                time.sleep(2)
                return retry(retry_attempts, spinner, 'Temporary authorization failure, please wait.')
            if api_response_code == 5002:
                time.sleep(2)
                return retry(retry_attempts, spinner, 'IMD is busy, please wait.')
            else:
                return retry(retry_attempts, spinner, f'{failure_message} | Response Code: {api_response_code}, IMD Error: {api_response_message}.')
                return False 
    except requests.exceptions.ConnectionError as error:
        return retry(retry_attempts, spinner, f'Error while interacting with IMD: \'{error}\'')

    return False

def apply_all_api_calls(config: dict, ordered_api_calls: list[dict]) ->  bool:
    retry_attempts: int = config['api_attempts']
    api_call_results: list = []
    for ordered_api_call in ordered_api_calls:
        for api_call in ordered_api_call['api_calls']:
            config_item_name: str = ordered_api_call['config_item_name']
            api_call_results.append(
                apply_api_call(config, config_item_name, api_call, retry_attempts)
            )
    all_api_calls_succeeded: bool = all(api_call_results)

    return all_api_calls_succeeded