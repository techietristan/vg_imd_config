import functools, re, sys

from typing import Pattern

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

def apply_format_function(config: dict, format_function: list, parsed_prompt_responses: list[dict]) -> str | dict:
    prompt_responses: dict = { response['config_item'] : response['value'] for response in parsed_prompt_responses }
   
    match format_function[0]:
        case 'apply_string_template':
            format_function_template: str = format_function[1]
            formatted_text: str = format_function_template.format(**prompt_responses)
            
    return formatted_text