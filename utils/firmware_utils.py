import os, requests, shutil, sys

from halo import Halo

from utils.prompt_utils import confirm

def download_firmware(config: dict) -> None:

    firmware_download_url: str = config['firmware_file_url']
    download_headers: dict = {'user-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    firmware_dir_path: str = f'{sys.argv[0]}/firmware/'
    parsed_firmware_url: dict = config['parsed_firmware_url']
    firmware_zip_filename: str = parsed_firmware_url['filename']
    firmware_filename: str = parsed_firmware_url['firmware_filename']
    firmware_zip_path: str = f'{firmware_dir_path}/{firmware_zip_filename}'
    firmware_file_path: str = f'{firmware_dir_path}{firmware_filename}'
    firmware_download_destination: str = f'{firmware_dir_path}{firmware_zip_filename}'
    firmware_zip_file_exists: bool = os.path.isfile(firmware_zip_path)
    firmware_file_exists: bool = os.path.isfile(firmware_file_path)
    download_timeout = config['download_timeout']

    print(f'{firmware_file_path}')

    if not firmware_zip_file_exists and confirm(config = config, confirm_prompt = 'Firmware file not found. Download firmware from the Virtiv website? '):
        status_message = Halo(text = 'Downloading firmware...', spinner = 'dots')
        status_message.start()
        try:
            firmware_request = requests.get(firmware_download_url, headers = download_headers, allow_redirects = True, timeout = download_timeout)
            with open(firmware_download_destination, 'wb') as zipped_firmware_file:
                zipped_firmware_file.write(firmware_request.content)
            shutil.unpack_archive(firmware_download_destination, firmware_dir_path)
            status_message.stop()
        except Exception as error:
            if confirm(f'Error downloading firmware file: {error}\n Try again?'):
                return download_firmware(config)
        print(f'Firmware downloaded and extracted to \'{firmware_dir_path}\'.')
    
    if firmware_zip_file_exists:
