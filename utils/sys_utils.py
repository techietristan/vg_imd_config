import os, sys

def exit_with_code(code: int):
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)