import sys

from utils.api_utils import get_firmware_version, login_to_imd, reset_imd_to_factory_defaults, set_imd_creds, upgrade_imd_firmware
from utils.argument_utils import parse_args
from utils.config_utils import get_config
from utils.firmware_utils import get_firmware_file_path

args = parse_args(sys.argv)
config = get_config(main_file = __file__, args = args)

if args.set_creds:
    set_imd_creds(config = config)

if args.get_firmware_version:
    current_firmware_version = get_firmware_version(config = config, print_result = True)

if args.reset_imd:
    reset_imd_to_factory_defaults(config = config, quiet = True)

if args.upgrade:
    firmware_file_path, firmware_filename = get_firmware_file_path(config = config)
    if bool(firmware_file_path):
        upgrade_imd_firmware(config = config, firmware_file_path = firmware_file_path, firmware_filename = firmware_filename, quiet = False)
