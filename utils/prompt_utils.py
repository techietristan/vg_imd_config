from utils.format_utils import format_bold, format_red
from utils.parse_utils import guess_next_hostname

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

def get_next_imd_config(config: dict, print_greeting: bool = True) -> bool:
    if print_greeting:
        print('Welcome to the Geist Vertiv IMD Configuration Script!\n')

    if 'current_pdu' not in config.keys():    
        row: str = input('Please enter the row number (e.g. \'4\'): ').zfill(2)
        rack: str = input('Please enter the rack number (e.g. \'7\'): ').zfill(2)
        pdu_letter: str = input('Please enter the PDU letter (e.g. \'b\'): ').upper()
        pdu_hostname: str = input('Please enter the PDU hostname (e.g. ab-012345-ps-b1): ')
        pdu_id: str = f'R{row}-{rack}/{pdu_letter}'
        
    else:
        current = config['current_pdu']
        row_guess = current['row']
        rack_guess = str(int(current['rack']) + 1).zfill(2) if current['pdu_letter'] == 'B' else current['rack']
        pdu_letter_guess = 'A' if current['pdu_letter'] == 'B' else 'B'
        pdu_hostname_guess = guess_next_hostname(config, current['pdu_hostname'])
        print(f'guessing {pdu_hostname_guess} from input of {current['pdu_hostname']}')

        row: str = input_with_default('Please enter the row number', row_guess).zfill(2)
        rack: str = input_with_default('Please enter the rack number', rack_guess).zfill(2)
        pdu_letter: str = input_with_default('Please enter the PDU letter', pdu_letter_guess).upper()
        pdu_hostname: str = input_with_default('Please enter the PDU hostname', pdu_hostname_guess)
        pdu_id: str = f'R{row}-{rack}/{pdu_letter}'
        
    username, password = get_credentials(config)
    confirm_prompt = f'\n\t{format_bold('Push this configuration to the currently connected IMD?')}\n\t{pdu_id}\n\t{pdu_hostname}\n\t{username}\n\n(y or n) :'
    push_config: bool = confirm(config, confirm_prompt)

    if push_config:
        config['current_pdu'] = {'row': row, 'rack': rack, 'pdu_letter': pdu_letter, 'pdu_id': pdu_id, 'pdu_hostname': pdu_hostname}
        return True
    elif confirm(config, 'Do you want to try again? (y or n): '):
        if confirm(config, 'Do you want to change the username and password? (y or n): '):
            update_credentials(config)
        return get_next_imd_config(config, print_greeting = False)
    else:
        return False

    

