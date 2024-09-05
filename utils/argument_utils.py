import argparse

def parse_args(system_arguments: list[str]):
    parser = argparse.ArgumentParser(
        prog = 'Vertiv™ Geist™ IMD Configuration Script',
        description = 'Unofficial script for configuring and upgrading Vertiv™ Geist™ IMDs'
    )

    parser.add_argument('-a', '--imd_ip_address',       help='Specify the IP address of the IMD to be configured.')
    parser.add_argument('-f', '--get_firmware_version', help='Get the firmware version of the currently connected IMD.', action='store_true')
    parser.add_argument('-u', '--upgrade',              help='Upgrade the firmware of the currently connected IMD.', action='store_true')

    return parser.parse_args()
