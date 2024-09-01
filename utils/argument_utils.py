import argparse

def parse_args(system_arguments):
    parser = argparse.ArgumentParser(
        prog = 'Vertiv™ Geist™ IMD Configuration Script',
        description = 'Unofficial script for configuring and upgrading Vertiv™ Geist™ IMDs'
    )

    parser.add_argument('-u', '--upgrade',      help='Upgrade the firmware of the currently connected IMD.')

    return parser.parse_args()
