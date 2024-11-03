import os, sys

from utils.format_utils import format_blue, format_yellow
from utils.prompt_utils import confirm

def exit_with_code(code: int) -> None:
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)

def remove_customized_files(config: dict, quiet: bool = False) -> None:
    default_files: list[str] = [ 'default_config.json', 'default_prompts.json', '.gitignore' ]
    default_files_path: str = config['config_files_path']
    config_dir_contents: list[str] = os.listdir(default_files_path)
    customized_files: list[str] = [ file for file in config_dir_contents if file not in default_files ]

    if confirm(config, f'Remove the following customized files?\n\t{ '\n\t'.join(format_yellow(file_name) for file_name in customized_files) }\n(y or n): '):
        for customized_file in customized_files:
            customized_file_path: str = os.path.join(default_files_path, customized_file)
            os.remove(customized_file_path)
            print(f'\tDeleted {format_blue(customized_file)}')



