import re, validators

from re import Match, Pattern
from typing import Any

from utils.format_utils import format_red
from utils.dict_utils import get_value_if_key_exists

def is_exactly(value: Any, expected_value: Any) -> bool:
    return type(value) == type(expected_value) and value == expected_value

def is_exactly_zero(value: Any) -> bool:
    return is_exactly(value, 0)

def is_exactly_one(value: Any) -> bool:
    return is_exactly(value, 1)

def is_valid(config: dict, regex: str, string: str) -> bool: 
    if type(string) != str:
        return False
    regex_match = re.match(regex, string)
    return not regex_match == None

def is_vaild_firmware_version(config: dict, firmware_version: str) -> bool:
    valid_firmware_regex: str = r'^[0-9]{1,2}.[0-9]{1,2}.[0-9]{1,2}$'
    return is_valid(config, valid_firmware_regex, firmware_version)

def is_valid_hostname(config: dict, hostname: str) -> bool:
    valid_hostname_regex: str = r'^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$'
    return is_valid(config, valid_hostname_regex, hostname)

def get_next_in_sequence(config: dict, current_suffix: str) -> str | None:
    if type(current_suffix) is not str:
        return None
    try:
        sequence: list = config['hostname_format']['sequence']
        lower_sequence: list = [ suffix.lower() for suffix in sequence ]
        lower_suffix: str = current_suffix.lower()
        current_suffix_is_upper_case: bool = current_suffix.isupper()
        sequence_last_index: int = len(sequence) - 1
        current_suffix_index = lower_sequence.index(lower_suffix)
        current_suffix_is_last_in_sequence: bool = current_suffix_index == sequence_last_index
        next_index_in_sequence: int = 0 if current_suffix_is_last_in_sequence else current_suffix_index + 1
        next_in_sequence: str = sequence[next_index_in_sequence]
        return next_in_sequence.upper() if current_suffix_is_upper_case else next_in_sequence
    except (KeyError, IndexError, ValueError):
        return None
       
def guess_next_hostname(config: dict, hostname: str) -> str | None:
    if not is_valid_hostname(config, hostname):
        return None
    try:
        hostname_format: dict = config['hostname_format']
        variable_index: int = hostname_format['variable_group_index']
        hostname_regex: Pattern = re.compile(hostname_format['hostname_regex'])
        regex_match: Match[str] | None = hostname_regex.match(hostname)
        hostname_parts: list = regex_match.groups() # type: ignore
        variable_suffix: str = hostname_parts[variable_index]
        next_in_sequence: str | None = get_next_in_sequence(config, variable_suffix)
        next_hostname_parts: list = [ 
            part 
            if index != variable_index 
            else next_in_sequence 
            for index, part in enumerate(hostname_parts) ]
        next_hostname: str = ''.join(next_hostname_parts)
        return next_hostname
    except (re.error, TypeError, KeyError, AttributeError):
        return None

def parse_firmware_url(config: dict, url: str) -> dict | bool:
    if type(url) is not str or not validators.url(url):
        return False
    try:
        url_components: list = url.split('/')
        url_path: str = f'{'/'.join(url_components[0:-1])}/'
        filename: str = url_components[-1]
        bare_filename: str = '.'.join(filename.split('.')[0:-1])
        firmware_filename: str = f'{'-'.join(bare_filename.split('-')[0:-1])}.firmware'
        extension: str = url_components[-1].split('.')[-1]

        parsed_url: dict = {
            'url': url,
            'url_path': url_path,
            'filename': filename,
            'firmware_filename': firmware_filename,
            'bare_filename': bare_filename,
            'extension': extension
        }
        return parsed_url
    except (IndexError, TypeError):
        return False

def run_verify_function(config: dict, user_input: str, verify_function: list) -> bool:
    stripped_user_input = user_input.strip()
    match verify_function[0]:
        case 'is_int':
            try:
                return bool(type(int(stripped_user_input)) == int)
            except ValueError:
                return False
        case 'is_one_of':
            return bool(stripped_user_input.lower() in verify_function[1])
        case 'is_between':
            return bool(int(verify_function[1]) <= len(user_input) <= int(verify_function[2]))
        case 'is_hostname':
            return bool(validators.hostname(stripped_user_input))
        case 'is_domain_name':
            return bool(validators.domain(stripped_user_input))
        case 'is_valid_username':
            return bool(re.fullmatch(r'[a-zA-Z][a-zA-Z0-9-_]{0,31}', stripped_user_input))
    return False

def verify_input(config: dict, input_params: dict, user_input: str) -> bool:
    verify_functions: list[list] = input_params['verify_functions']
    empty_allowed: bool = bool(input_params['empty_allowed'])
    if user_input == '':
        return True if empty_allowed else False
    elif bool(verify_functions[0]):
        verify_function_results: list[bool] = [
            run_verify_function(config, user_input, verify_function)
            for verify_function in verify_functions
        ]
        return all(verify_function_results)
    else:
        return True

def apply_user_input_formatting_function(config: dict, format_function: list, current_formatting: str) -> str:
    match format_function[0]:
        case 'zfill':
            return current_formatting.zfill(format_function[1])
        case 'lower':
            return current_formatting.lower()
        case 'upper':
            return current_formatting.upper()
    return current_formatting

def apply_user_input_formatting_functions(config: dict, format_functions: list[list], next_formatting: str, iteration = 0) -> str:
    number_of_format_functions: int = len(format_functions)
    try:
        if iteration + 1 == number_of_format_functions:
            return apply_user_input_formatting_function(config, format_functions[iteration], next_formatting)
        else:
            next_formatting = apply_user_input_formatting_function(config, format_functions[iteration], next_formatting)
            return apply_user_input_formatting_functions(config, format_functions, next_formatting, iteration + 1)
    except IndexError:
        return next_formatting

def format_user_input(config: dict, input_params: dict, user_input: str) -> str:
    format_functions: list[list] = input_params['format_functions']
    stripped_user_input = user_input.strip()
    if bool(format_functions[0]):
        return apply_user_input_formatting_functions(config, format_functions, stripped_user_input)
    else:
        return stripped_user_input

def apply_format_function(config: dict, format_function: list, parsed_prompt_responses: dict) -> str:
    match format_function[0]:
        case 'apply_template':
            format_function_template: str = format_function[1]
            format_function_keys: list = [ format_function_key for format_function_key in format_function[2] ]
            prompt_responses: dict = { response['config_item'] : response['value'] for response in parsed_prompt_responses }
            formatted_string: str = format_function_template.format(**prompt_responses)
            return formatted_string
    return ''

def has_unspecified_default(prompt: dict) -> bool:
    try:
        is_unique_value: bool = is_exactly_one(prompt['unique_value'])
        has_default_value: bool = bool(prompt['default_value'])
        default_is_unspecified: bool = not is_unique_value and not has_default_value
        return default_is_unspecified
    except KeyError:
        return False

def contains_unspecified_defaults(prompts: list[dict]) -> bool:
    unspecified_defaults: list[bool] = [
        has_unspecified_default(prompt)
        for prompt in prompts ]
    return any(unspecified_defaults)

def has_encrypted_default(prompt: dict) -> bool:
    encrypt_default: bool = is_exactly_one(get_value_if_key_exists(prompt, 'encrypt_default'))
    salt: bool = bool(get_value_if_key_exists(prompt, 'salt'))
    default_value: bool = bool(get_value_if_key_exists(prompt, 'default_value'))
    return bool(encrypt_default and salt and default_value)

def contains_encrypted_defaults(prompts: list[dict]) -> bool:
    return bool( True in [ has_encrypted_default(prompt) for prompt in prompts ])