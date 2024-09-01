import os, requests

def download_firmware(config):
    firmware_download_url = f'{config['firmware_file_url']}{config['firmware_filename']}'
    download_headers = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
