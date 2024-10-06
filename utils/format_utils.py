import sys

format_escape_strings: dict = {
    'red':      '\033[91m',
    'green':    '\033[92m',
    'yellow':   '\033[93m',
    'blue':     '\033[94m',
}

def format_color(color: str, text: str):
    color_sequence = format_escape_strings[color]
    end_sequence = '\033[00m'

    return f'{color_sequence}{text}{end_sequence}'

def format_red(text: str):
    return format_color('red', text)

def format_yellow(text: str):
    return format_color('yellow', text)

def format_green(text: str):
    return format_color('green', text)

def format_blue(text: str):
    return format_color('blue', text)

def format_bold(text: str):
    return f'\033[1m{text}\033[0m'

def clear_line():
    sys.stdout.write('\x1b[2K')