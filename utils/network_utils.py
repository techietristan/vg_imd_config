import os, subprocess

from utils.format_utils import format_blue
from utils.prompt_utils import confirm

def host_pings(config: dict, hostname: str, attempts_remaining: int = 10, quiet: bool = False) -> bool:
    if attempts_remaining == 0:
        return False

    is_windows: bool = os.sys.platform.lower() ==  'win32' #type: ignore[attr-defined]
    count_param: str = '-n' if is_windows else '-c'
    host_is_pinging: bool = subprocess.run(
        ['ping', count_param, '1', hostname],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL         
    ).returncode == 0

    if host_is_pinging:
        return True
    
    if not quiet: print(f'Awaiting response from IMD at {format_blue(hostname)}.')  

    return host_pings(config, hostname, attempts_remaining -1, True)

def wait_for_ping(config: dict, quiet: bool = False) -> bool:
    imd_ip_address: str = config['current_imd_ip']
    if host_pings(config, imd_ip_address, 10, quiet):
        return True
    if not quiet and confirm(config, f'Unable to reach IMD at {format_blue(imd_ip_address)}. Try again? (y or n): '):
        return wait_for_ping(config, quiet)

    return False