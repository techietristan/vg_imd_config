import re

def is_vaild_firmware_version(firmware_version_string):
    firmware_regex = r'^\d{1,2}.\d{1,2}.\d{1,2}$'
    firmware_match = re.match(firmware_regex, firmware_version_string)
    return not firmware_match == None