import os, sys

def exit_with_code(code: int) -> None:
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)