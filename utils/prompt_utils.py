from utils.format_utils import format_red

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
    return input('Please enter the username: ')

def get_password(config: dict) -> str:
    password = getpass('Please enter the password: ')
    confirm_password = getpass('Please enter the password again: ')

    if password == confirm_password:
        return password
    else:
        print("Passwords do not match. Please try again.")
        get_password(config)

def get_credentials(config: dict) -> tuple:
    try:
        username = config['username']
        password = config['password']
    except KeyError:
        username = get_username(config)
        password = get_password(config)
        config['username'], config['password'] = username, password
    
    config['username'], config['password'] = username, password

    return username, password

