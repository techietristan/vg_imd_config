from unittest import mock, TestCase

import utils.prompt_utils

class TestConfirm(TestCase):
    @mock.patch('utils.prompt_utils.input', create = True)
    def test_confirm_returns_true(self, mock_input):
        positive_responses=['Yes', 'yes', 'ye', 'yE', 'y', 'Y', 'YES']
        for positive_response in positive_responses:
            mock_input.side_effect=[positive_response]
            returned_value = utils.prompt_utils.confirm({},'prompt', False)
            self.assertTrue(returned_value)

    @mock.patch('utils.prompt_utils.input', create = True)
    def test_confirm_returns_false(self, mock_input):
        negative_responses=['No', 'no', 'n', 'nO', 'N', 'NO']
        for negative_response in negative_responses:
            mock_input.side_effect=[negative_response]
            returned_value = utils.prompt_utils.confirm({},'prompt', False)
            self.assertFalse(returned_value)

class TestGetUsername(TestCase):
    @mock.patch('utils.prompt_utils.input', create = True)
    def test_get_username_returns_string(self, mock_input):
        mock_input.side_effect=['test_username']
        returned_value = utils.prompt_utils.get_username({})
        self.assertEqual(type(returned_value), str)

    @mock.patch('utils.prompt_utils.input', create = True)
    def test_get_username_returns_stripped_input(self, mock_input):
        usernames_with_spaces = [' test_username', ' test_username ', 'test_username ']
        for username_with_spaces in usernames_with_spaces:
            mock_input.side_effect=[username_with_spaces]
            returned_value = utils.prompt_utils.get_username({})
            self.assertEqual('test_username', returned_value)

class TestGetPassword(TestCase):
    @mock.patch('utils.prompt_utils.getpass', create = True)
    def test_get_password_returns_string(self, mock_input):
        mock_input.side_effect=['same_password', 'same_password']
        returned_value = utils.prompt_utils.get_password({}, quiet = True)
        self.assertEqual(type(returned_value), str)

    @mock.patch('utils.prompt_utils.getpass', create = True)    
    def test_get_password_returns_password(self, mock_input):
        mock_input.side_effect=['same_password', 'same_password']
        returned_value = utils.prompt_utils.get_password({}, quiet = True)
        self.assertEqual(returned_value, 'same_password')

    @mock.patch('utils.prompt_utils.getpass', create = True)    
    def test_get_password_retries_on_mismatch(self, mock_input):
        mock_input.side_effect=['some_password', 'different_password', 'same_password', 'same_password']
        returned_value = utils.prompt_utils.get_password({}, quiet = True)
        self.assertEqual(returned_value, 'same_password')
        
class TestGetCredentials(TestCase):
    def test_get_credentials_returns_current_creds(self):
        self.config_with_creds = {
            'username': 'test_username',
            'password': 'test_password'
        }
        returned_creds = utils.prompt_utils.get_credentials(self.config_with_creds)
        self.assertEqual(returned_creds, ('test_username', 'test_password'))

class TestGetInput(TestCase):
    def test_get_input_none(self):
        test_input = utils.prompt_utils.get_input(config = {}, input_type = 'none', simulated_user_input = 'test_input' )
        self.assertEqual(test_input, 'test_input')
    def test_get_input_none_with_default(self):
        test_input = utils.prompt_utils.get_input(config = {}, input_type = 'none', default_value = 'default_value', simulated_user_input = '' )
        self.assertEqual(test_input, 'default_value')

class TestValidateSelection(TestCase):
    test_options: list[str] = [ 'option_1', 'option_2', 'option_3' ]

    def test_validate_selection_valid(self):
        test_selection: int = utils.prompt_utils.validate_selection(self.test_options, '2')
        self.assertEqual(test_selection, 1 )

class TestEnumerateOptions(TestCase):
    @mock.patch('utils.prompt_utils.input', create = True)
    def test_enumerate_options_returns_correct_option(self, mock_input):
        test_options: list = [
            'option_1', 'option_2', 'option_3'
        ]
        mock_input.side_effect=['2']
        returned_option = utils.prompt_utils.enumerate_options({}, test_options, '', True)
        self.assertEqual(returned_option, 'option_2')

class TestGetPromptFunction(TestCase):
    def test_get_prompt_function_zfill(self):
        input_params = {
            "config_item": "row",
            "config_item_name": "Rack Row",
            "prompt_text": "rack row",
            "example_text": "7",
            "verify_functions": [["is_int"]],
            "format_functions": [["zfill", 2]],
            "input_mode": "input",
            "default_value": "",
            "api_calls": [""],
            "empty_allowed": 0,
            "required": 1,
            "test": 1
        }
        expected_return_dict = {
            "config_item": "row",
            "config_item_name": "Rack Row",
            "api_calls": [""],
            "value": "07",
            "test": 1
        }  
        returned_function = utils.prompt_utils.get_prompt_function({}, input_params, quiet = True)
        self.assertDictEqual(returned_function({}, '7'), expected_return_dict)

    def test_get_prompt_function_lower(self):
        input_params = {
            "config_item": "pdu_letter",
            "config_item_name": "PDU Letter",
            "prompt_text": "PDU letter",
            "example_text": "b",
            "verify_functions": [["is_one_of", ["a", "b"]]],
            "format_functions": [["lower"]],
            "input_mode": "input",
            "default_value": "",
            "api_calls": [""],
            "empty_allowed": 0,
            "required": 1,
            "test": 1
        }
        expected_return_dict = {
            "config_item": "pdu_letter",
            "config_item_name": "PDU Letter",
            "api_calls": [""],
            "value": "b",
            "test": 1
        }  
        returned_function = utils.prompt_utils.get_prompt_function({}, input_params, quiet = True)
        self.assertDictEqual(returned_function({}, 'B'), expected_return_dict)

    def test_get_prompt_function_valid_input(self):
        input_params = {
            "config_item": "row",
            "config_item_name": "Rack Row",
            "prompt_text": "rack row",
            "example_text": "7",
            "verify_functions": [["is_int"]],
            "format_functions": [["zfill", 2]],
            "input_mode": "input",
            "default_value": "",
            "api_calls": [""],
            "empty_allowed": 0,
            "required": 1,
            "test": 0
        }
        returned_function = utils.prompt_utils.get_prompt_function({}, input_params, quiet = True)
        self.assertTrue(callable(returned_function))

    def test_get_prompt_function_missing_required_keys(self):
        input_params = {
            "config_item_name": "Rack Row",
            "prompt_text": "rack row",
            "example_text": "7",
            "verify_functions": [["is_int"]],
            "format_functions": [["zfill", 2]],
            "api_calls": [""],
            "empty_allowed": 0,
            "required": 1,
            "test": 1
        }
        returned_function = utils.prompt_utils.get_prompt_function({}, input_params, quiet = True)
        self.assertFalse(returned_function)
