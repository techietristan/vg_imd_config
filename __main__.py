import sys

from utils.api_utils import get_firmware_version
from utils.argument_utils import parse_args
from utils.config_utils import get_config

args = parse_args(sys.argv)
config = get_config(main_file = __file__, args = args)

if args.get_firmware_version:
    current_firmware_version = get_firmware_version(config = config, print_result = True)