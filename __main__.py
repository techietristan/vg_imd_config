import os, sys

from utils.api_utils import get_firmware_version, login_to_imd, reset_imd_to_factory_defaults, set_imd_creds, upgrade_imd_firmware
from utils.argument_utils import parse_args
from utils.config_utils import get_config

args = parse_args(sys.argv)
config = get_config(main_file = __file__, args = args)

try:
    if args.get_firmware_version:
        get_firmware_version(config = config, print_result = True)
        sys.exit(0)

    if args.reset_imd:
        reset_imd_to_factory_defaults(config = config)

    if args.set_password:
        set_imd_creds(config = config)

    if args.upgrade:
        upgrade_imd_firmware(config = config, quiet = False)


except KeyboardInterrupt:
    print('Exiting Script')
    try:
        sys.exit(130)
    except SystemExit:
        os._exit(130)