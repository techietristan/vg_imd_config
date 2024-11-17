import argparse

from argparse import Namespace

def parse_args(system_arguments: list[str]) -> Namespace:
    parser = argparse.ArgumentParser(
        prog = 'Vertiv™ Geist™ IMD Configuration Script',
        description = 'Unofficial script for configuring and upgrading Vertiv™ Geist™ IMDs'
    )

    parser.add_argument('-a', '--imd_ip_address',       help='Specify the IP address of the IMD to be configured.')
    parser.add_argument('-c', '--config_file',          help='Specify the configuration file to use.')
    parser.add_argument('-f', '--get_firmware_version', help='Get the firmware version of the currently connected IMD.', action='store_true')
    parser.add_argument('-p', '--set_password',         help='Set the username and password for the currently connected IMD.', action='store_true')
    parser.add_argument('-r', '--reset_imd',            help='Reset the currently connected IMD to factory defaults.', action='store_true')
    parser.add_argument('-u', '--upgrade',              help='Upgrade the firmware of the currently connected IMD.', action='store_true')

    parser.add_argument('--prompts_file',           help='Specify the interactive prompts file to use.')
    parser.add_argument('--reset_script',           help='Remove all customized config and prompts files leaving only the default templates for these files.', action='store_true')
    parser.add_argument('--skip_firmware_check',    help='Don\'t check the current IMD firmware version.', action = 'store_true')
    parser.add_argument('--spinner',                help='Set the spinner to use during lengthy script operations (see https://github.com/manrajgrover/halo).')
    

    return parser.parse_args()
