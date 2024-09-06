import re

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
    except Exception:
        return None