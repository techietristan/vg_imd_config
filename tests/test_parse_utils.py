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
    is_int_input_params: dict = {
        "verify_function": ["is_int"],
        "empty_allowed": 0
    }
    is_one_of_input_params: dict = {
        "verify_function": ["is_one_of", ["a", "b"]],
        "empty_allowed": 0
    }
    is_int_input_params_empty_allowed: dict = {
        "verify_function": ["is_int"],
        "empty_allowed": 1
    }
    is_one_of_input_params_empty_allowed: dict = {
        "verify_function": ["is_one_of", ["a", "b"]],
        "empty_allowed": 1
    }
    is_between_input_params: dict = {
        "verify_function": ["is_between", 1, 300],
        "empty_allowed": 0
    }
    is_hostname_input_params: dict = {
        "verify_function": ["is_hostname"],
        "empty_allowed": 0
    }
    is_domain_name_input_params: dict = {
        "verify_function": ["is_domain_name"],
        "empty_allowed": 0
    }
    is_valid_username_input_params: dict = {
        "verify_function": ["is_valid_username"],
        "empty_allowed": 0
    }
    no_verify_function_params_empty_allowed: dict = {
        "verify_function": [],
        "empty_allowed": 1
    }
    no_verify_function_params_empty_not_allowed: dict = {
        "verify_function": [],
        "empty_allowed": 0
    }

    def test_verify_input_valid_int(self):
        valid_result = verify_input({}, self.is_int_input_params, '4')
        self.assertTrue(valid_result)
    def test_verify_input_invalid_int(self):
        invalid_result = verify_input({}, self.is_int_input_params, 'abc')
        self.assertFalse(invalid_result)
    def test_verify_input_is_one_of(self):
        valid_result = verify_input({}, self.is_one_of_input_params, 'A')
        self.assertTrue(valid_result)
    def test_verify_input_is_not_one_of(self):
        invalid_result = verify_input({}, self.is_one_of_input_params, 'C')
        self.assertFalse(invalid_result)
    def test_verify_input_is_int_input_params_empty_allowed(self):
        valid_result = verify_input({}, self.is_int_input_params_empty_allowed, '')
        self.assertTrue(valid_result)
    def test_verify_input_is_one_of_input_params_empty_allowed(self):
        valid_result = verify_input({}, self.is_one_of_input_params_empty_allowed, '')
        self.assertTrue(valid_result)
    def test_verify_input_is_hostname(self):
        valid_hostnames = [
            'host-name',
            'hostname',
            'hostname123',
            '123hostname',
            'host123name',
            '123-hostname'
        ]
        invalid_hostnames = [
            'hostname_with_underscores',
            '-hostname-starting-with-hyphen',
            'hostname with spaces',
            'hostname-ending-with-hyphen-',
            'hostname-thats-just-too-damn-long-with-way-too-many-characters-to-be-considered-valid',
            'hostname@with(invalid)Chars',
            '',
        ]
        for valid_hostname in valid_hostnames:
            self.assertTrue(verify_input({}, self.is_hostname_input_params, valid_hostname))
        for invalid_hostname in invalid_hostnames:
            self.assertFalse(verify_input({}, self.is_hostname_input_params, invalid_hostname))
    def test_verify_input_is_domain_name(self):
        valid_domain_names = [
            'time.ntp.com',
            'this.is.a.long.but.valid.domain.name',
            'abc.biz',
            'time.co.uk',
            'google.com',
            'www.google.com',
            'pool.0.ntp.org',
            'pool.1.ntp.org'
        ]
        invalid_domain_names = [
            'domain with spaces',
            'domain.that.frankly.is.more.than.the.allowed.255.characters.and.is.therefore.not.valid.' * 5,
            'domain.name.#$%.with.invalid.chars.&*()@#$%^.fun',
            '',
        ]
        for valid_domain_name in valid_domain_names:
            self.assertTrue(verify_input({}, self.is_domain_name_input_params, valid_domain_name))
        for invalid_domain_name in invalid_domain_names:
            self.assertFalse(verify_input({}, self.is_domain_name_input_params, invalid_domain_name))
    def test_verify_input_is_valid_username(self):
        valid_usernames = [
            'valid_username',
            'valid_username-with-hypens123-',
            'vALiD-UsErN4M3',
            'username',
            'u'
        ]
        invalid_usernames = [
            'username with spaces',
            'username_with_more_than_32_chars0',
            '-username_starting_hyphen',
            '_username_starting_underscore',
            'username_with@#$%^invalid&*(chars)'
        ]
        for valid_username in valid_usernames:
            self.assertTrue(verify_input({}, self.is_valid_username_input_params, valid_username))
        for invalid_username in invalid_usernames:
            self.assertFalse(verify_input({}, self.is_valid_username_input_params, invalid_username))

    def test_is_between(self):
        valid_inputs = [
            ' ',
            'abcde12345' * 30,
            '23456&*()_fjkldsaLKJ'
        ]
        invalid_inputs = [
            '',
            'abcde12345' * 31,
        ]
        for valid_input in valid_inputs:
            self.assertTrue(verify_input({}, self.is_between_input_params, valid_input))
        for invalid_input in invalid_inputs:
            self.assertFalse(verify_input({}, self.is_between_input_params, invalid_input))

    def test_verify_input_no_verify_function_params_empty_allowed(self):
        valid_results = [
            'test_string',
            'test string with spaces',
            'm1x of numb3rs and letters',
            '',
            'LoWerR, UpPer, !@#$% **(Chars)'
        ]
        for valid_result in valid_results:
            self.assertTrue(verify_input({}, self.no_verify_function_params_empty_allowed, valid_result))
    def test_verify_input_no_verify_function_params_empty_not_allowed(self):
        valid_results = [
            'test_string',
            'test string with spaces'
            'm1x of numb3rs and letters',
            'LoWerR, UpPer, !@#$% **(Chars)'
        ]
        invalid_result = ''
        for valid_result in valid_results:
            self.assertTrue(verify_input({}, self.no_verify_function_params_empty_not_allowed, valid_result))
        self.assertFalse(verify_input({}, self.no_verify_function_params_empty_not_allowed, invalid_result))

class TestFormatUserInput(TestCase):
    def test_format_user_input_none(self):
        test_prompt = {'format_function': [], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'test_input ')
        self.assertEqual(formatted_user_input, 'test_input')
    def test_format_user_input_zfill(self):
        test_prompt = {'format_function': ['zfill', 2], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, '7 ')
        self.assertEqual(formatted_user_input, '07')
    def test_format_user_input_lower(self):
        test_prompt = {'format_function': ['lower'], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'TEST INPUT ')
        self.assertEqual(formatted_user_input, 'test input')
    def test_format_user_input_upper(self):
        test_prompt = {'format_function': ['upper'], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'test input ')
        self.assertEqual(formatted_user_input, 'TEST INPUT')  