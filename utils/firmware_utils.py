import functools, os, requests, shutil, sys, time #type: ignore[import-untyped]
from halo import Halo #type: ignore[import-untyped]
from tqdm.auto import tqdm #type: ignore[import-untyped]

from utils.api_utils import login_to_imd
from utils.dict_utils import get_value_if_key_exists
from utils.format_utils import format_blue, format_red, truncate_message
from utils.network_utils import wait_for_ping
from utils.parse_utils import is_vaild_firmware_version, version_is_higher
from utils.prompt_utils import confirm, get_credentials
from utils.spinner_utils import get_spinner

def download_and_extract_firmware(config: dict, firmware_download_destination: str, firmware_dir_path) -> bool:
    firmware_download_url: str = config['firmware_file_url']
    download_headers: dict = {'user-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    download_timeout: int = config['download_timeout']
    try:
        firmware_request = requests.get(firmware_download_url, headers = download_headers, stream = True, allow_redirects = True, timeout = download_timeout)
        if firmware_request.status_code != 200:
            firmware_request.raise_for_status()
            raise RuntimeError(f'Error while attempting to download firmware file: {firmware_request.status_code}')
        firmware_file_size: int = int(firmware_request.headers.get('Content-Length', 0))
        desc: str = '(Unknown total file size)' if firmware_file_size == 0 else ''
        firmware_request.raw.read = functools.partial(firmware_request.raw.read, decode_content = True) # type: ignore
        with tqdm.wrapattr(firmware_request.raw, 'read', total = firmware_file_size, desc = desc) as firmware_request_raw:
            with open(firmware_download_destination, 'wb') as zipped_firmware_file:
                shutil.copyfileobj(firmware_request_raw, zipped_firmware_file)
        shutil.unpack_archive(firmware_download_destination, firmware_dir_path)
        return True
    except Exception as error:
        if confirm(config, f'Error downloading firmware file: {error}\n Try again?', error = True):
                return download_and_extract_firmware(config, firmware_download_destination , firmware_dir_path)
        else:
            return False

def get_firmware_file_path(config: dict) -> tuple[str, str] | tuple[bool, bool]:
    parsed_firmware_url: dict = config['parsed_firmware_url']
    firmware_dir_path: str = f'{sys.argv[0]}/firmware/'
    bare_filename: str = parsed_firmware_url['bare_filename']
    firmware_zip_filename: str = parsed_firmware_url['filename']
    firmware_zip_path: str = f'{firmware_dir_path}/{firmware_zip_filename}'
    firmware_zip_file_exists: bool = os.path.isfile(firmware_zip_path)
    firmware_filename: str = parsed_firmware_url['firmware_filename']
    firmware_file_path: str = f'{firmware_dir_path}{bare_filename}/{firmware_filename}'
    firmware_file_exists: bool = os.path.isfile(firmware_file_path)
    firmware_download_destination: str = f'{firmware_dir_path}{firmware_zip_filename}'

    if not firmware_zip_file_exists and not firmware_file_exists and confirm(config = config, 
    confirm_prompt = 'Firmware file not found. Download and extract firmware from the Vertiv website? '):
        try:
            download_and_extract_firmware(config = config, firmware_download_destination = firmware_download_destination, firmware_dir_path = firmware_dir_path)
        except Exception as download_error:
            if confirm(config, f'Error downloading firmware file: {download_error}\n Try again?', error = True):
                return get_firmware_file_path(config)
            else:
                return False, False
    if firmware_zip_file_exists and not firmware_file_exists and confirm(config = config, 
    confirm_prompt = 'Compressed firmware file found. Do you want to extract it?'):
        try:
            shutil.unpack_archive(firmware_download_destination, firmware_dir_path)
            print(f'Firmware extracted to \'{firmware_dir_path}\'.')
        except Exception as error:
            if confirm(config, f'Error extracting firmware file: {error}\n Try again?', error = True):
                return get_firmware_file_path(config)
            else:
                return False, False
    return firmware_file_path, firmware_filename

def get_firmware_version(config: dict, quiet: bool = False) -> str | bool:
    spinner: Halo = Halo(text = 'Checking current IMD firmware version...\n', spinner = get_spinner(config))
    api_url: str = config['api_base_url']
    api_firmware_url: str= f'{api_url}sys/version'
    headers: dict = config['headers']

    try:
        if not quiet: spinner.start()
        if wait_for_ping(config, quiet = True):
            firmware_response: dict = requests.get(api_firmware_url, headers = headers, verify = False).json()
            response_code: int = firmware_response['retCode']
            response_message: str = firmware_response['retMsg']
            firmware_version: str = firmware_response['data']
            if response_code == 0 and is_vaild_firmware_version(config = config, firmware_version = firmware_version):
                if not quiet:
                    time.sleep(1)
                    spinner.succeed(f'\nCurrent IMD Firmware Version: {format_blue(firmware_version)}')
                return firmware_version
            else:
                if not quiet: spinner.fail(truncate_message(response_message))
                raise Exception(firmware_response)
        else: 
            if not quiet: 
                spinner.fail('Unable to reach IMD.')
                if confirm(config, 'Do you want to try again? (y or n): '):
                    return get_firmware_version(config, quiet)

    except Exception as error:
        if not quiet: 
            spinner.fail(truncate_message(f'Unable to get IMD firmware version: {error}'))
            if confirm(config, confirm_prompt = 'Do you want to try again?: '):
                return get_firmware_version(config = config, quiet = quiet)
    return False

def wait_for_firmware_upgrade(config: dict, target_firmware_version: str | bool, wait_time_in_seconds: int = 10) -> bool:
    current_firmware_version: str | bool = get_firmware_version(config, True)
    if current_firmware_version != target_firmware_version:
        time.sleep(wait_time_in_seconds)
        return wait_for_firmware_upgrade(config, target_firmware_version, wait_time_in_seconds)
    return True

def upgrade_imd_firmware(config: dict, target_firmware_version: str | bool, firmware_file_path: str | bool, token: str | bool, quiet: bool = False) -> bool:
    firmware_upgrade_api_endpoint: str = f'https://{config['current_imd_ip']}/transfer/firmware?token={token}'
    firmware_upgrade_headers: dict = {'Content_Type' : 'multipart/form-data'}
    spinner: Halo = Halo(text = f'Uploading Firmware v.{format_blue(target_firmware_version)}\n', spinner = get_spinner(config)) #type: ignore[arg-type]

    try:
        if not quiet: spinner.start()
        with open(firmware_file_path, 'rb') as file_bytes:
            requests.post(
                firmware_upgrade_api_endpoint, 
                headers = firmware_upgrade_headers, 
                files = { 'firmware_file': file_bytes },
                verify = False)
            if not quiet: spinner.succeed('Firmware file uploaded successfully, please wait while the IMD restarts.')
            time.sleep(60)
            wait_for_firmware_upgrade(config, target_firmware_version, 10)
            return True
    except Exception as firmware_upgrade_error:
        if not quiet: spinner.fail(truncate_message(f'\n Error upgrading firmware: {firmware_upgrade_error}'))
        if not confirm(config, '\nDo you want to try again (y or n): '): 
            return True
        upgrade_imd_firmware(config, target_firmware_version, firmware_file_path, token)
    return False

def prompt_to_upgrade_imd_firmware(config: dict, quiet: bool = True) -> bool:
    current_firmware_version: str | bool = get_firmware_version(config, quiet = True)
    target_firmware_version: str | bool = get_value_if_key_exists(config, 'firmware_target')
    if type(current_firmware_version) == bool and not quiet:
        print(format_red('Unable to get current firmware version.'))
        if confirm(config, 'Do you want to try again? (y or n): '):
            return prompt_to_upgrade_imd_firmware(config, quiet = quiet)
    if current_firmware_version == target_firmware_version and type(current_firmware_version) == str:
        if not quiet: print(f'IMD firmware up to date (v.{format_blue(current_firmware_version)}).') #type: ignore[arg-type]
        return True
    current_firmware_lower_than_target: bool = version_is_higher(target_firmware_version, current_firmware_version) #type: ignore[arg-type]
    if current_firmware_lower_than_target:
        if not confirm(config, f'Current IMD firmware version is {format_blue(current_firmware_version)}.\nUpgrade to {format_blue(target_firmware_version)}? (y or n): '): return True#type: ignore[arg-type]
        firmware_file_path, firmware_filename = get_firmware_file_path(config = config)
        if not bool(firmware_file_path):
            if not quiet: print(format_red('Unable to find or download firmware. Please check your configuration.'))
            return False
        username, password = get_credentials(config)
        token: str | bool = login_to_imd(config, quiet = True)
        if bool(token):
            return upgrade_imd_firmware(config, target_firmware_version, firmware_file_path, token, quiet)
    return False