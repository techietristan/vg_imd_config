from unittest import TestCase

from utils.parse_utils import is_vaild_firmware_version, is_valid_hostname, get_next_in_sequence, guess_next_hostname, parse_firmware_url, verify_input, format_user_input
test_config: dict = {
    "hostname_format": {
        "hostname_regex": "(.+)([a,b,A,B])(\\d)$",
        "variable_group_index": 1,
        "sequence": ['a', 'b']
    }
}

class TestIsValidFirmwareVersion(TestCase):

    def test_is_valid_firmware_version_valid_string(self):
        self.assertTrue(is_vaild_firmware_version(test_config, '1.2.3'))
        self.assertTrue(is_vaild_firmware_version(test_config, '01.02.03'))
        self.assertTrue(is_vaild_firmware_version(test_config, '10.02.33'))
        self.assertTrue(is_vaild_firmware_version(test_config, '10.2.33'))

    def test_is_valid_firmware_version_invalid_chars(self):
        self.assertFalse(is_vaild_firmware_version(test_config, 'a.b.c'))
        self.assertFalse(is_vaild_firmware_version(test_config, '10.b.c'))
        self.assertFalse(is_vaild_firmware_version(test_config, '01.b.3'))

    def test_is_valid_firmware_version_invalid_type(self):
        self.assertFalse(is_vaild_firmware_version(test_config, None))
        self.assertFalse(is_vaild_firmware_version(test_config, False))
        self.assertFalse(is_vaild_firmware_version(test_config, 3.3))
        self.assertFalse(is_vaild_firmware_version(test_config, {'key': 'value'}))

class TestIsValidHostname(TestCase):

    def test_is_valid_hostname_valid(self):
        self.assertTrue(is_valid_hostname(test_config, 'test-hostname-r'))
        self.assertTrue(is_valid_hostname(test_config, 'testhostname'))
        self.assertTrue(is_valid_hostname(test_config, 'TestHostname'))
        self.assertTrue(is_valid_hostname(test_config, 'Test-Hostname123'))
        self.assertTrue(is_valid_hostname(test_config, 'test-hostname-123-r'))

    def test_is_valid_hostname_spaces(self):
        self.assertFalse(is_valid_hostname(test_config, 'test hostname'))
        self.assertFalse(is_valid_hostname(test_config, ' test hostname'))
        self.assertFalse(is_valid_hostname(test_config, 'test hostname '))
        self.assertFalse(is_valid_hostname(test_config, 'test_hostname '))
        self.assertFalse(is_valid_hostname(test_config, ' test_hostname'))
    
    def test_is_valid_hostname_illegal_chars(self):
        self.assertFalse(is_valid_hostname(test_config, 'test*hostname'))
        self.assertFalse(is_valid_hostname(test_config, '?test$hostname'))
        self.assertFalse(is_valid_hostname(test_config, 'test/hostname'))
        self.assertFalse(is_valid_hostname(test_config, 'Test_Hostname'))
        self.assertFalse(is_valid_hostname(test_config, 'test-hostname+'))

class TestGetNextInSequence(TestCase):
    
    def test_get_next_in_sequence_invalid_arguments(self):

        self.invalid_config: dict = {
            "hostname_format": {
                "hostname_regex": "(.+)(-)(a,b,A,B)(\\d)$",
                "variable_group": 3,
                "sequence": []
            }
        }

        self.assertIsNone(get_next_in_sequence({}, 'a'))
        self.assertIsNone(get_next_in_sequence({}, 1))
        self.assertIsNone(get_next_in_sequence(self.invalid_config, 'a'))
        self.assertIsNone(get_next_in_sequence(self.invalid_config, 'B'))     

    def test_get_next_in_sequence_valid_arguments(self):
        self.assertEqual(get_next_in_sequence(test_config, 'a'), 'b')
        self.assertEqual(get_next_in_sequence(test_config, 'b'), 'a')
        self.assertEqual(get_next_in_sequence(test_config, 'B'), 'A')
        self.assertEqual(get_next_in_sequence(test_config, 'A'), 'B')

class TestGuessNextHostname(TestCase):

    def test_guess_next_hostname_invalid(self):
        self.assertIsNone(guess_next_hostname(test_config, 'hostname a'))
        self.assertIsNone(guess_next_hostname(test_config, 'HOSTNAME A'))
        self.assertIsNone(guess_next_hostname(test_config, 'hostname%'))
        self.assertIsNone(guess_next_hostname(test_config, 'HOSTNAME*A'))
    
    def test_guess_next_hostname_suffix(self):
        self.assertEqual(guess_next_hostname(test_config, 'hostname-a1'), 'hostname-b1')
        self.assertEqual(guess_next_hostname(test_config, 'HOSTNAME-A1'), 'HOSTNAME-B1')
        self.assertEqual(guess_next_hostname(test_config, 'hostname123-a1'), 'hostname123-b1')
        self.assertEqual(guess_next_hostname(test_config, 'HOSTNAME123-A1'), 'HOSTNAME123-B1')
        self.assertEqual(guess_next_hostname(test_config, 'ab-hostname-a1'), 'ab-hostname-b1')
        self.assertEqual(guess_next_hostname(test_config, 'AB-HOSTNAME-A1'), 'AB-HOSTNAME-B1')
        self.assertEqual(guess_next_hostname(test_config, 'ab-0123hostname-a1'), 'ab-0123hostname-b1')
        self.assertEqual(guess_next_hostname(test_config, 'AB-0123HOSTNAME-A1'), 'AB-0123HOSTNAME-B1')
        self.assertEqual(guess_next_hostname(test_config, 'hostname-b1'), 'hostname-a1')
        self.assertEqual(guess_next_hostname(test_config, 'HOSTNAME-B1'), 'HOSTNAME-A1')
        self.assertEqual(guess_next_hostname(test_config, 'hostname-ps-a1'), 'hostname-ps-b1')
        self.assertEqual(guess_next_hostname(test_config, 'HOSTNAME-ps-A1'), 'HOSTNAME-ps-B1')
        self.assertEqual(guess_next_hostname(test_config, 'ab-012345-ps-a1'), 'ab-012345-ps-b1')
    
    def test_guess_next_hostname_exception(self):
        self.assertRaises(TypeError, guess_next_hostname({}, 'hostname-ps-a1'))
        self.assertRaises(TypeError, guess_next_hostname({}, {'test_key': 'test_value'}))
        self.assertRaises(TypeError, guess_next_hostname(test_config, 'hostname-ps-a1'))

class TestParseFirmwareUrl(TestCase):

    good_url: dict = {
        'url': 'https://www.vertiv.com/49aa2a/globalassets/documents/geist-i03-6_1_2-04302024.zip',
        'url_path': 'https://www.vertiv.com/49aa2a/globalassets/documents/',
        'filename': 'geist-i03-6_1_2-04302024.zip',
        'firmware_filename': 'geist-i03-6_1_2.firmware',
        'bare_filename': 'geist-i03-6_1_2-04302024',
        'extension': 'zip'
    }

    good_url_periods: dict = {
        'url': 'https://www.test.com/first/second/third/test-filename.with.periods.ext',
        'url_path': 'https://www.test.com/first/second/third/',
        'filename': 'test-filename.with.periods.ext',
        'firmware_filename': 'test.firmware',
        'bare_filename': 'test-filename.with.periods',
        'extension': 'ext'
    }

    invalid_url: str = 'invalid url string'
    invalid_url_type: list = []
    unparseable_url: str = 'https://some.unparsable.url/cant/parse/this'


    def test_parse_firmware_url_valid(self):
        self.assertEqual(parse_firmware_url({}, self.good_url['url']), self.good_url)
    
    def test_parse_firmware_url_periods(self):
        self.assertEqual(parse_firmware_url({}, self.good_url_periods['url']), self.good_url_periods)
    
    def test_parse_firmware_url_invalid(self):
        self.assertFalse(parse_firmware_url({}, self.invalid_url))
    
    def test_parse_firmware_url_invalid_type(self):
        self.assertFalse(parse_firmware_url({}, self.invalid_url_type))
    
    def test_parse_firmware_raises_exception(self):
        self.assertRaises(TypeError, parse_firmware_url({}, self.unparseable_url))
    

class TestVerifyInput(TestCase):
    def test_verify_input_valid_int(self):
        valid_result = verify_input({}, ['is_int'], '4')
        self.assertTrue(valid_result)
    def test_verify_input_invalid_int(self):
        invalid_result = verify_input({}, ['is_int'], 'abc')
        self.assertFalse(invalid_result)
    def test_verify_input_is_one_of(self):
        valid_result = verify_input({}, ['is_one_of', ['a','b']], 'A')
        self.assertTrue(valid_result)
    def test_verify_input_is_not_one_of(self):
        invalid_result = verify_input({}, ['is_one_of', ['a','b']], 'C')
        self.assertFalse(invalid_result)

class TestFormatUserInput(TestCase):
    def test_format_user_input_none(self):
        formatted_user_input = format_user_input({}, [], 'test_input ')
        self.assertEqual(formatted_user_input, 'test_input')
    def test_format_user_input_zfill(self):
        formatted_user_input = format_user_input({}, ['zfill', 2], '7 ')
        self.assertEqual(formatted_user_input, '07')
    def test_format_user_input_lower(self):
        formatted_user_input = format_user_input({}, ['lower'], 'TEST INPUT ')
        self.assertEqual(formatted_user_input, 'test input')  