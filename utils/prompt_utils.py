from utils.format_utils import format_bold, format_red, clear_line
from utils.parse_utils import guess_next_hostname, verify_input, format_user_input

import json
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
            print(format_red('Passwords do not match. Please try again.'))
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

def get_input(config: dict, input_type: str = 'input', formatted_prompt_text: str = '', default_value: str = '', simulated_user_input: str | bool = None):
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

def get_prompt_function(config: dict, input_params: dict, quiet = False):
    try:
        config_item =       input_params['config_item']
        input_mode =        input_params['input_mode']
        prompt_text =       input_params['prompt_text']
        example_text =      input_params['example_text']
        default_value =     input_params['default_value']
        api_path =          input_params['api_path']
        test =              input_params['test']
    except KeyError as error:
        if not quiet:
            print(format_red(f'Invalid Prompt Input: {error}.'))
        return False
    
    input_type: str = 'none' if bool(test) else 'getpass' if input_mode == 'getpass' else 'input'
    default_or_example: str = f'(press \'Enter\' to use \'{default_value}\')' if bool(default_value) else f'(e.g. \'{example_text}\')'
    formatted_prompt_text = f'Please enter the {prompt_text}{default_or_example}: '

    def prompt_function(config: dict = config, simulated_user_input: str | bool = None):
        user_input = get_input(config = config, input_type = input_type, formatted_prompt_text = formatted_prompt_text, default_value = default_value, simulated_user_input = simulated_user_input)
        formatted_user_input = format_user_input(config = config, input_params = input_params, user_input = user_input)
        is_valid_input = verify_input(config = config, input_params = input_params, user_input = user_input)
        if not is_valid_input:
            clear_line()
            if not quiet:
                invalid_input_warning: str = 'Invalid Password.' if input_type == 'getpass' else f'Invalid Input:\'{user_input}\''
                print(format_red(invalid_input_warning))
            return prompt_function(config = config, simulated_user_input = simulated_user_input)
        return {
            "config_item": config_item,
            "api_path": api_path,
            "value": formatted_user_input,
            "test": test
        }

    return prompt_function

def get_next_imd_config(config: dict = {}, prompts_file_path: str = 'config/default_prompts.json'):
    with open(prompts_file_path, 'r') as prompts_file:
        prompts: dict = json.load(prompts_file)
        if bool(prompts['greeting']['display']):
            print(format_bold(prompts['greeting']['text']))

        imd_config_functions: list = [
            get_prompt_function(config = config, input_params = prompt, quiet = False)
            for prompt in prompts['prompts']
        ]
        next_imd_config: list = [
            config_item(config = config) for config_item in imd_config_functions 
        ]
    
    return next_imd_config