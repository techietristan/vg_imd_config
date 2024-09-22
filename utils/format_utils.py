import sys

def format_red(text: str):
    return "\033[91m{}\033[00m".format(text)

def format_bold(text: str):
    return "\033[1m{}\033[0m".format(text)

def clear_line():
    sys.stdout.write('\x1b[2K')