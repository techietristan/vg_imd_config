def print_red(text: str):
    print("\033[91m{}\033[00m".format(text))

def format_red(text: str):
    return "\033[91m{}\033[00m".format(text)

def format_bold(text: str):
    return "\033[1m{}\033[0m".format(text)