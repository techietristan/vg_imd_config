import json, requests
from utils.format_utils import print_red
from utils.parse_utils import is_vaild_firmware_version

def get_firmware_version(config, print_result = False):
    api_url = config['api_base_url']
    api_firmware_url = f'{api_url}sys/version'
    headers = config['headers']

    try:
        firmware_response = requests.get(api_firmware_url, headers).json()
        response_code = firmware_response['retCode']
        firmware_version = firmware_response['data']
        if response_code == 0 and is_vaild_firmware_version(firmware_version):
            if print_result:
                print(f'Current IMD Firmware Version: {firmware_version}')
            return firmware_version
        else:
            raise Exception(firmware_response)
    except:
        print_red('Unable to get IMD firmware version.\nPlease ensure you are able to ping the IMD.')
        return "Unknown"