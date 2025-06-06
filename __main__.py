import sys

from argparse import Namespace

from utils.api_utils import get_ordered_api_calls, reset_imd_to_factory_defaults, set_imd_creds, apply_all_api_calls
from utils.argument_utils import parse_args
from utils.config_utils import get_config, update_prompts_file_with_defaults, write_current_imd_config_to_file, get_previous_imd_config, remove_previous_imd_config
from utils.encryption_utils import decrypt_prompts
from utils.firmware_utils import get_firmware_version, prompt_to_upgrade_imd_firmware
from utils.format_utils import format_blue, format_yellow
from utils.network_utils import wait_for_ping
from utils.prompt_utils import get_unique_config_items, confirm, confirm_imd_config
from utils.sys_utils import exit_with_code, remove_customized_files

def main(config: dict = {}) -> int:
    args: Namespace = parse_args(sys.argv)
    quiet_flags: list[str] = ['get_firmware_version', 'reset_imd', 'set_password', 'upgrade', 'reset_script']
    quiet: bool = any(vars(args)[quiet_flag] is not False for quiet_flag in quiet_flags)
    skip_firmware_check = args.skip_firmware_check

    try:
        config = get_config(main_file = __file__, args = args, quiet = quiet) if not bool(config) else config
        if   args.get_firmware_version: get_firmware_version(config = config, quiet = False)
        elif args.reset_imd:            reset_imd_to_factory_defaults(config = config, quiet = False)
        elif args.set_password:         set_imd_creds(config = config, quiet = False)
        elif args.upgrade:              prompt_to_upgrade_imd_firmware(config = config, quiet = False)
        elif args.reset_script:         remove_customized_files(config, quiet = False)    

        else:
            update_prompts_file_with_defaults(config)
            prompts: dict = decrypt_prompts(config)
            previous_imd_config: list[dict] | bool = get_previous_imd_config(config)
            if bool(previous_imd_config): ordered_api_calls: list[dict] = previous_imd_config #type: ignore[assignment]
            else:
                unique_config_items: list[dict] = get_unique_config_items(config, prompts)
                ordered_api_calls = get_ordered_api_calls(config, prompts, unique_config_items)
                write_current_imd_config_to_file(config, ordered_api_calls, quiet = False)
            if confirm_imd_config(config, ordered_api_calls) and wait_for_ping(config):
                if not skip_firmware_check and not prompt_to_upgrade_imd_firmware(config = config, quiet = False):
                    if not confirm(config, 'Do you want to continue with the configuration? (y or n): '):
                        print(format_blue('Exiting Script'))
                        exit_with_code(0)
                if wait_for_ping(config) and apply_all_api_calls(config, ordered_api_calls):
                    remove_previous_imd_config(config)
                    previous_imd_config = False 
                    print('\nIMD configuration successful!')
            if bool(previous_imd_config) and confirm(config, 'Would you like to delete this configuration? (y or n): '): remove_previous_imd_config(config)
            if confirm(config, 'Would you like to configure another IMD? (y or n): '): main(config)
            
        print(format_blue('Exiting Script'))
        exit_with_code(0)

    except KeyboardInterrupt:
        print(format_yellow('\nKeyboard Interrupt Received. Exiting Script'))
        exit_with_code(130)

    return 0

if __name__ == "__main__":
    main()