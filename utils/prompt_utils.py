from utils.format_utils import format_bold, format_red
from utils.parse_utils import guess_next_hostname, verify_input, format_user_input

from getpass import getpass

def confirm(config: dict = {}, confirm_prompt: str = '', error = False) -> bool:
    prompt = format_red(confirm_prompt) if error else confirm_prompt
    user_response = input(prompt).lower().strip()
    affirmative_responses = ['yes', 'ye', 'y']
    negative_responses = ['no', 'n']
    response_is_positive: bool = user_response in affirmative_responses
    response_is_negative: bool = user_response in negative_responses
    invalid_response_prompt: str = 'Invlaid response, please enter \'y\' or \'n\': '

    return True if response_is_positive else False if response_is_negative else confirm(invalid_response_prompt)

def get_username(config: dict) -> str:
    return input('Please enter the username: ').strip()

def get_password(config: dict, quiet = False) -> str:
    password: str = getpass('Please enter the password: ')
    confirm_password: str = getpass('Please enter the password again: ')

    if password == confirm_password: 
        return password
    else:
        if not quiet:
            print("Passwords do not match. Please try again.")
        return get_password(config)

def update_credentials(config: dict) -> None:
    username = get_username(config)
    password = get_password(config)
    config['username'] = username
    config['password'] = password

def get_credentials(config: dict) -> tuple:
    if 'password' not in config.keys():
        update_credentials(config)
    return config['username'], config['password']

def input_with_default(prompt: str, default: str) -> None:
    user_input = input(f'{prompt} (press ENTER to use {default}): ')
    return default if user_input == '' else user_input

def get_input(config: dict, input_type: str = 'input', simulated_user_input: str | bool = None):
    match input_type:
        case 'input':
            user_input = input(formatted_prompt_text)
        case 'getpass':
            user_input = getpass(formatted_prompt_text)
        case 'none':
            user_input = simulated_user_input
    return user_input

def get_prompt_function(config: dict, input_params: dict):
    try:
        config_item =       input_params['config_item']
        input_mode =        input_params['input_mode']
        prompt_text =       input_params['prompt_text']
        example_text =      input_params['example_text']
        verify_function =   input_params['verify_function']
        format_function =   input_params['format_function']
        api_path =          input_params['api_path']
        test =              input_params['test']
    except KeyError as error:
        print(format_red(f'Invalid Prompt Input: {error}.'))
        return False
    
    input_type = 'none' if bool(test) else 'getpass' if input_mode == 'getpass' else 'input'
    formatted_prompt_text = f'Please enter the {prompt_text} (e.g. \'{example_text}\'): '

    def prompt_function(config: dict = config, simulated_user_input: str | bool = None):
        user_input = get_input(config = config, input_type = input_type, simulated_user_input = simulated_user_input)
        formatted_user_input = format_user_input(config = config, format_function = format_function, user_input = user_input)
        is_valid_input = verify_input(config = config, verify_function = verify_function, user_input = formatted_user_input)
        if not is_valid_input:
            return prompt_function(config = config, simulated_user_input = simulated_user_input)
        return {
            "config_item": config_item,
            "api_path": api_path,
            "value": formatted_user_input,
            "test": test
        }

    return prompt_function