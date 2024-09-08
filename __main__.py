import sys

from utils.api_utils import get_firmware_version, login_to_imd, reset_imd_to_factory_defaults, set_imd_creds
from utils.argument_utils import parse_args
from utils.config_utils import get_config
from utils.firmware_utils import get_firmware_file_path

args = parse_args(sys.argv)
config = get_config(main_file = __file__, args = args)

if args.get_firmware_version:
    current_firmware_version = get_firmware_version(config = config, print_result = True)

if args.reset_imd:
    reset_imd_to_factory_defaults(config = config, quiet = True)

if args.upgrade:
    firmware_file_path: str = get_firmware_file_path(config = config)