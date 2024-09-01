import sys

from utils.argument_utils import parse_args
from utils.config_utils import get_config

args = parse_args(sys.argv)
config = get_config(main_file = __file__)
