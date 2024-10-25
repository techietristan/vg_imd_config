import os, sys

from utils.api_utils import get_firmware_version, reset_imd_to_factory_defaults, set_imd_creds, upgrade_imd_firmware
from utils.argument_utils import parse_args
from utils.config_utils import get_config, update_prompts_file_with_defaults
from utils.encryption_utils import decrypt_prompts
from utils.format_utils import format_yellow
from utils.prompt_utils import get_next_imd_config
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
            next_imd_config: list[dict] = get_next_imd_config(config, prompts)

            config['current_imd_config'] = next_imd_config

            print(next_imd_config)

    except KeyboardInterrupt:
        print(format_yellow('\nKeyboard Interrupt Received. Exiting Script'))
        exit_with_code(130)


if __name__ == "__main__":
    main()