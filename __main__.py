import os, sys

from utils.api_utils import get_firmware_version, reset_imd_to_factory_defaults, set_imd_creds, upgrade_imd_firmware
from utils.argument_utils import parse_args
from utils.config_utils import get_config
from utils.prompt_utils import get_next_imd_config

def main():
    try:
        args = parse_args(sys.argv)
        config = get_config(main_file = __file__, args = args, quiet = True)

        if args.get_firmware_version:
            get_firmware_version(config = config, print_result = True)
            sys.exit(0)

        if args.reset_imd:
            reset_imd_to_factory_defaults(config = config, quiet = False)

        if args.set_password:
            set_imd_creds(config = config, quiet = False)

        if args.upgrade:
            upgrade_imd_firmware(config = config, quiet = False)

        if not any (bool(value) for value in vars(args).values()):
            print(config)

    except KeyboardInterrupt:
        print('\nKeyboard Interrupt Received. Exiting Script')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)


if __name__ == "__main__":
    main()