import re

def is_vaild_firmware_version(firmware_version: str) -> bool:
    if type(firmware_version) != str:
        return False
    firmware_regex = r'^\d{1,2}.\d{1,2}.\d{1,2}$'
    firmware_match = re.match(firmware_regex, firmware_version)
    return not firmware_match == None