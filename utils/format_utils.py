import sys

from utils.dict_utils import get_value_if_key_exists

format_escape_strings: dict = {
    'red':      '\033[91m',
    'green':    '\033[92m',
    'yellow':   '\033[93m',
    'blue':     '\033[94m',
}

def format_color(color: str, text: str) -> str:
    color_sequence = format_escape_strings[color]
    end_sequence = '\033[00m'

    return f'{color_sequence}{text}{end_sequence}'

def format_red(text: str) -> str:
    return format_color('red', text)

def format_yellow(text: str) -> str:
    return format_color('yellow', text)

def format_green(text: str) -> str:
    return format_color('green', text)

def format_blue(text: str) -> str:
    return format_color('blue', text)

def format_bold(text: str) -> str:
    return f'\033[1m{text}\033[0m'

def clear_line() -> None:
    sys.stdout.write('\x1b[2K')

def apply_formatting_function(config: dict, format_function: list, current_formatting: str = '', config_items: list[dict] = [{}]) -> str:
    if bool(format_function):
        match format_function[0]:
            case 'zfill':
                return current_formatting.zfill(format_function[1])
            case 'lower':
                return current_formatting.lower()
            case 'upper':
                return current_formatting.upper()
            case 'replace':
                existing_char, target_char = format_function[1], format_function[2]
                return current_formatting.replace(existing_char, target_char)
            case 'apply_string_template':
                if bool(config_items):
                    config_values: dict = { item['config_item'] : get_value_if_key_exists(item, 'value') for item in config_items }
                    format_function_template: str = format_function[1]
                    return format_function_template.format(**config_values)
    return current_formatting

def apply_formatting_functions(config: dict, format_functions: list[list], next_formatting: str = '', config_items: list[dict] = [{}], iteration = 0) -> str:
    number_of_format_functions: int = len(format_functions)
    try:
        if iteration + 1 == number_of_format_functions:
            return apply_formatting_function(config, format_functions[iteration], next_formatting, config_items)
        else:
            next_formatting = apply_formatting_function(config, format_functions[iteration], next_formatting, config_items)
            return apply_formatting_functions(config, format_functions, next_formatting, config_items, iteration + 1)
    except IndexError:
        return next_formatting

def format_user_input(config: dict, input_params: dict, user_input: str) -> str:
    format_functions: list[list] | bool = get_value_if_key_exists(input_params, 'format_functions')
    stripped_user_input = user_input.strip()
    if bool(format_functions):
        return apply_formatting_functions(config, format_functions, stripped_user_input) #type: ignore[arg-type]
    else:
        return stripped_user_input

def get_value_to_display(config: dict, formatter:dict, config_items: list[dict]) -> str | None:
    raw_value_to_display: str | bool = get_value_if_key_exists(formatter, 'value_to_display')
    if bool(raw_value_to_display):
        value_to_display: str = apply_formatting_function(config, ['apply_string_template', raw_value_to_display], '', config_items )  
        return value_to_display if bool(value_to_display) else None
    return None 
                
def get_formatted_config_items(config: dict, prompts: dict, config_items: list[dict]) -> list[dict]:
    formatters: list[dict] = prompts['formatters']
    formatted_config_items: list[dict] = [
        {  
            'config_item': formatter['config_item'],
            'config_item_name': formatter['config_item_name'],
            'display_to_user': bool(get_value_if_key_exists(formatter, 'display_to_user')),
            'value_to_display': get_value_to_display(config, formatter, config_items),
            'api_calls': [ {
                'cmd': api_call['cmd'],
                'method': api_call['method'],
                'api_path': api_call['api_path'],
                'data': apply_formatting_functions(config, formatter['format_functions'], '', config_items)
            } for api_call in formatter['api_calls'] ]
        }
        for formatter in formatters ]

    return formatted_config_items

def get_status_messages(config: dict, config_item_name: str, command: str) -> tuple[str, ...]:
    command_adds: bool = bool(command == 'set' or command == 'add')
    command_removes: bool = bool(command == 'delete')
    status_message: str =   f'Setting {format_yellow(config_item_name)}\n'          if command_adds else f'Removing {format_yellow(config_item_name)}\n'            if command_removes else ''
    success_message: str =  f'{format_blue(config_item_name)} set successfully!'    if command_adds else f'{format_blue(config_item_name)} removed successfully!'   if command_removes else ''
    failure_message: str =  f'Failed to set {format_red(config_item_name)}!'        if command_adds else f'Failed to remove {format_red(config_item_name)}!'        if command_removes else ''

    return status_message, success_message, failure_message