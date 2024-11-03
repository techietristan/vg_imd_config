from utils.dict_utils import get_value_if_key_exists
from utils.format_utils import format_bold, format_red, format_blue, clear_line, format_user_input
from utils.parse_utils import verify_input, is_exactly_one, is_boolean_false

from getpass import getpass
from typing import Callable

def confirm(config: dict = {}, confirm_prompt: str = '', error = False) -> bool:
    prompt = format_red(confirm_prompt) if error else confirm_prompt
    user_response = input(prompt).lower().strip()
    affirmative_responses = ['yes', 'ye', 'y']
    negative_responses = ['no', 'n']
    response_is_positive: bool = user_response in affirmative_responses
    response_is_negative: bool = user_response in negative_responses
    invalid_response_prompt: str = format_red('Invlaid response, please enter \'y\' or \'n\': ')

    return True if response_is_positive else False if response_is_negative else confirm(config = config, confirm_prompt = invalid_response_prompt)

def get_input(
        config: dict, 
        input_type: str = 'input', 
        formatted_prompt_text: str = '', 
        default_value: str = '', 
        simulated_user_input: str = '', 
        confirm_input: bool = True):
    match input_type:
        case 'input':
            user_input: str = input(formatted_prompt_text)   
        case 'getpass':
            user_input = get_password(config = config, prompt_text = formatted_prompt_text, confirm_input = confirm_input, quiet = False)
        case 'none':
            user_input = simulated_user_input
    if user_input.strip() == '':
        if bool(default_value):
            return default_value
        else:
            print(format_red('Empty input is not allowed. Please enter a valid value.'))
            return get_input(config, input_type, formatted_prompt_text, default_value, simulated_user_input, confirm_input)
    if bool(user_input):
        return user_input
    else:
        print(format_red('Invalid input. Please enter a valid value.'))
        return get_input(config, input_type, formatted_prompt_text, default_value, simulated_user_input, confirm_input)

def get_username(config: dict) -> str:
    return input('Please enter the username: ').strip()

def get_password(config: dict, prompt_text: str = 'Please enter the password', confirm_input: bool = True, quiet = False) -> str:
    password: str = getpass(f'{prompt_text}: ')
    if bool(confirm_input):
        confirm_password: str = getpass(f'{prompt_text} again: ')
        if password != confirm_password: 
            if not quiet: print(format_red('Passwords do not match. Please try again.'))
            return get_password(config, prompt_text, confirm_input, quiet)            

    return password

def update_credentials(config: dict) -> None:
    username = get_username(config)
    password = get_password(config)
    config['username'] = username
    config['password'] = password

def get_credentials(config: dict) -> tuple:
    if 'password' not in config.keys():
        update_credentials(config)
    return config['username'], config['password']


def validate_selection(options: list[str], selection: str = '') -> int:
    if not bool(selection):
        selection = get_input({}).strip()
    number_of_options: int = len(options)
    try:
        selection_int: int = int(selection) - 1
    except ValueError:
        print(format_red(f'Invalid input: {selection}.'))
        return validate_selection(options, selection)
    if not 0 <= selection_int < number_of_options:
        print(format_red(f'Please enter a number between 1 and {number_of_options}.'))
        return validate_selection(options)
    return selection_int

def enumerate_options(config: dict, options: list[str], prompt: str = '', quiet = False) -> str:
    default_prompt: str = 'Please select from the following options:'
    prompt_text: str = prompt if bool(prompt) else default_prompt
    if bool(prompt) and not quiet:
        print(format_bold(prompt_text))
        for index, option in enumerate(options, 1):
            print(f'{index}. {option}')
    selection_index: int = validate_selection(options)
    return options[selection_index]

def update_config(config: dict, config_item: str, formatted_user_input: str) -> None:
    keys_to_auto_update: list[str] = [ 'username', 'password', 'hostname', 'location' ] 
    if config_item in keys_to_auto_update: config[config_item] = formatted_user_input
    return
       
def get_prompt_function(config: dict, input_params: dict, quiet: bool = False) -> Callable | bool:
    try:
        config_item =       input_params['config_item']
        prompt_text =       input_params['prompt_text']
        example_text =      input_params['example_text']
        default_value =     get_value_if_key_exists(input_params, 'default_value')
        input_mode =        get_value_if_key_exists(input_params, 'input_mode')
        test =              get_value_if_key_exists(input_params, 'test')
        
        input_type: str = 'none' if bool(test) else 'getpass' if input_mode == 'getpass' else 'input'
        default_or_example: str = f'(press \'Enter\' to use \'{format_blue(default_value)}\')' if bool(default_value) else f'(e.g. \'{format_blue(example_text)}\')'
        formatted_prompt_text: str = (f'Please enter the password (Press \'Enter\' to use the {format_blue('default password')})' 
            if input_mode == 'getpass' 
            else f'Please enter the {prompt_text} {default_or_example}: ')
        confirm_input: bool = False if input_mode == 'getpass' and bool(default_value) else True

        def prompt_function(config: dict = config, simulated_user_input: str = ''):
            user_input = get_input(config = config, input_type = input_type, formatted_prompt_text = formatted_prompt_text, default_value = default_value, simulated_user_input = simulated_user_input, confirm_input = confirm_input)
            formatted_user_input = format_user_input(config = config, input_params = input_params, user_input = user_input)
            is_valid_input = verify_input(config = config, input_params = input_params, user_input = user_input)
            if not is_valid_input:
                clear_line()
                invalid_input_warning: str = 'Invalid Password.' if input_type == 'getpass' else f'Invalid Input:\'{user_input}\''
                if not quiet: print(format_red(invalid_input_warning))
                return prompt_function(config = config, simulated_user_input = simulated_user_input)
            update_config(config, config_item, formatted_user_input)

            return {
                "config_item": config_item,
                "value": formatted_user_input,
                "test": test if not is_boolean_false(test) else 0
            }

        return prompt_function

    except KeyError as key_error:
        if not quiet:
            print(format_red(f'The prompts file is missing required keys: {key_error}'))
        return False

def get_unique_config_items(config: dict, prompts: dict, quiet = False) -> list[dict]:
    if bool(prompts['greeting']['display']) and is_exactly_one(config['display_greeting']):
        print(format_bold(prompts['greeting']['text']))
        prompts['greeting']['display'] = 0

    imd_config_functions: list = [
        get_prompt_function(config = config, input_params = prompt, quiet = quiet)
        for prompt in prompts['prompts']
    ]
    unique_config_items: list[dict] = [ config_item(config = config) for config_item in imd_config_functions ]

    return unique_config_items

def confirm_imd_config(config: dict, ordered_api_calls: list[dict]) -> bool:
    confirm_items: list[dict] = [
        {'config_item_name': api_call['config_item_name'], 'value_to_display': api_call['value_to_display']}
        for api_call in ordered_api_calls
        if bool(get_value_if_key_exists(api_call, 'value_to_display')) and bool (get_value_if_key_exists(api_call, 'display_to_user'))
    ]
    print('\nConfigure the currently connected IMD with the following parameters?\n')
    for confirm_item in confirm_items:
        print(f'\t{confirm_item['config_item_name']}: {format_blue(confirm_item['value_to_display'])}')
    imd_config_confirmed: bool = confirm(config, '\nPlease enter \'y\' or \'n\': ')

    return imd_config_confirmed
