import unittest

from utils.parse_utils import is_vaild_firmware_version

class test_is_valid_firmware_version(unittest.TestCase):

    def test_is_valid_firmware_version_valid_string(self):
        self.assertTrue(is_vaild_firmware_version('1.2.3'))
        self.assertTrue(is_vaild_firmware_version('01.02.03'))
        self.assertTrue(is_vaild_firmware_version('10.02.33'))
        self.assertTrue(is_vaild_firmware_version('10.2.33'))
        
    def test_is_valid_firmware_version_invalid_chars(self):
        self.assertFalse(is_vaild_firmware_version('a.b.c'))
        self.assertFalse(is_vaild_firmware_version('10.b.c'))
        self.assertFalse(is_vaild_firmware_version('01.b.3'))

    def test_is_valid_firmware_version_invalid_type(self):
        self.assertFalse(is_vaild_firmware_version(None))
        self.assertFalse(is_vaild_firmware_version(False))
        self.assertFalse(is_vaild_firmware_version(3.3))
        self.assertFalse(is_vaild_firmware_version({'key': 'value'}))