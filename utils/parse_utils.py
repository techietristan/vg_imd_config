import re, validators

def is_valid(config: dict, regex: str, string: str): 
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
        hostname_regex: str = re.compile(hostname_format['hostname_regex'])
        regex_match: list = hostname_regex.match(hostname)
        hostname_parts: list = regex_match.groups()
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

def verify_input(config: dict, input_params: dict, user_input: str) -> bool:
    verify_function: list = input_params['verify_function']
    empty_allowed: bool = bool(input_params['empty_allowed'])
    stripped_user_input = user_input.strip()
    if user_input == '':
        return True if empty_allowed else False
    elif bool(verify_function):
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
                return validators.hostname(stripped_user_input)
            case 'is_domain_name':
                return validators.domain(stripped_user_input)
            case 'is_valid_username':
                return bool(re.fullmatch(r'[a-zA-Z][a-zA-Z0-9-_]{0,31}', stripped_user_input))
    else:
        return True


def format_user_input(config: dict, input_params: dict, user_input: str) -> str:
    format_function: list = input_params['format_function']
    stripped_user_input = user_input.strip()
    if bool(format_function):
        match format_function[0]:
            case 'zfill':
                formatted_user_input = stripped_user_input.zfill(format_function[1])
            case 'lower':
                formatted_user_input = stripped_user_input.lower()
            case 'upper':
                formatted_user_input = stripped_user_input.upper()
    else:
        formatted_user_input = stripped_user_input
    
    return formatted_user_input