import functools, os, requests, shutil, sys
from tqdm.auto import tqdm
from utils.prompt_utils import confirm

def download_and_extract_firmware(config: dict, firmware_download_destination: str, firmware_dir_path) -> bool:
    firmware_download_url: str = config['firmware_file_url']
    download_headers: dict = {'user-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    download_timeout: int = config['download_timeout']
    try:
        firmware_request = requests.get(firmware_download_url, headers = download_headers, stream = True, allow_redirects = True, timeout = download_timeout)
        if firmware_request.status_code != 200:
            firmware_request.raise_for_status()
            raise RuntimeError(f'Error while attemping to download firmware file: {firmware_request.status_code}')
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
    confirm_prompt = 'Firmware file not found. Download and extract firmware from the Virtiv website? '):
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
