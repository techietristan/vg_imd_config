import os, sys

from utils.api_utils import get_firmware_version, get_ordered_api_calls, reset_imd_to_factory_defaults, set_imd_creds, upgrade_imd_firmware
from utils.argument_utils import parse_args
from utils.config_utils import get_config, update_prompts_file_with_defaults, write_current_imd_config_to_file, get_previous_imd_config
from utils.encryption_utils import decrypt_prompts
from utils.format_utils import format_yellow
from utils.prompt_utils import get_unique_config_items, confirm_imd_config
from utils.sys_utils import exit_with_code

def main():
    try:
        args = parse_args(sys.argv)
        
        if args.get_firmware_version:
            get_firmware_version(config = config, print_result = True)

        elif args.reset_imd:
            reset_imd_to_factory_defaults(config = config, quiet = False)

        elif args.set_password:
            set_imd_creds(config = config, quiet = False)

        elif args.upgrade:
            upgrade_imd_firmware(config = config, quiet = False)
        
        elif not any (bool(value) for value in vars(args).values()):
            config: dict = get_config(main_file = __file__, args = args, quiet = False)
            update_prompts_file_with_defaults(config)
            prompts: dict = decrypt_prompts(config)
            previous_imd_config: dict | bool = get_previous_imd_config(config)

            if bool(previous_imd_config):
                ordered_api_calls: list[dict] = previous_imd_config
            else:
                unique_config_items: list[dict] = get_unique_config_items(config, prompts)
                ordered_api_calls: list[dict] = get_ordered_api_calls(config, prompts, unique_config_items)
                write_current_imd_config_to_file(config, ordered_api_calls, quiet = False)
            if bool(confirm_imd_config(config, ordered_api_calls)):
                print(format_yellow('Proceed to configure IMD'))


    except KeyboardInterrupt:
        print(format_yellow('\nKeyboard Interrupt Received. Exiting Script'))
        exit_with_code(130)

if __name__ == "__main__":
    main()