def print_red(text: str):
    print("\033[91m{}\033[00m".format(text))

def format_red(text: str):
    return "\033[91m{}\033[00m".format(text)