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

class TestInputWithDefault(TestCase):
    @mock.patch('utils.prompt_utils.input', create = True)
    def test_input_with_default_returns_default(self, mock_input):
        mock_input.side_effect = ['']
        returned_value = utils.prompt_utils.input_with_default('prompt', 'default_value')
        self.assertEqual('default_value', returned_value)

    @mock.patch('utils.prompt_utils.input', create = True)
    def test_input_with_default_returns_input(self, mock_input):
        mock_input.side_effect = ['user_input']
        returned_value = utils.prompt_utils.input_with_default('prompt', 'default_value')
        self.assertEqual('user_input', returned_value)

class TestGetNextImdConfig(TestCase):
    @mock.patch('utils.prompt_utils.input', create = True)
    def test_get_next_imd_config_creds_no_current_pdu(self, mock_input):
        config_to_update = {
            'username': 'test_username',
            'password': 'test_password'
        }
        expected_config = {
            'username': 'test_username',
            'password': 'test_password',
            'current_pdu': {
                'row': '04', 
                'rack': '07', 
                'pdu_letter': 'B', 
                'pdu_id': 'R04-07/B', 
                'pdu_hostname': 'ab-012345-ps-b1'
            }
        }
        mock_input.side_effect = ['4', '7', 'b', 'ab-012345-ps-b1', 'y']
        return_value = utils.prompt_utils.get_next_imd_config(config_to_update, False)
        self.assertEqual(config_to_update, expected_config)
        self.assertTrue(return_value)

    @mock.patch('utils.prompt_utils.input', create = True)
    @mock.patch('utils.prompt_utils.getpass', create = True)
    def test_get_next_imd_config_no_creds_no_current_pdu(self, mock_getpass, mock_input):
        config_to_update = {}
        expected_config = {
            'username': 'test_username',
            'password': 'test_password',
            'current_pdu': {
                'row': '04', 
                'rack': '07', 
                'pdu_letter': 'B', 
                'pdu_id': 'R04-07/B', 
                'pdu_hostname': 'ab-012345-ps-b1'
            }
        }
        mock_getpass.side_effect = ['test_password', 'test_password']
        mock_input.side_effect = ['4', '7', 'b', 'ab-012345-ps-b1', 'test_username', 'y']
        return_value = utils.prompt_utils.get_next_imd_config(config_to_update, False)
        self.assertEqual(config_to_update, expected_config)
        self.assertTrue(return_value)

    @mock.patch('utils.prompt_utils.input', create = True)
    @mock.patch('utils.prompt_utils.getpass', create = True)
    def test_get_next_imd_config_no_creds_current_pdu_guesses_current_cab(self, mock_getpass, mock_input):
        config_to_update = {
            "hostname_format": {
                "hostname_regex": "(.+)([a,b,A,B])(\\d)$",
                "variable_group_index": 1,
                "sequence": ["a", "b"]
            },
            'current_pdu': {
                'row': '04', 
                'rack': '07', 
                'pdu_letter': 'A', 
                'pdu_id': 'R04-07/A', 
                'pdu_hostname': 'ab-012345-ps-a1'
        }}
        expected_config = {
            "hostname_format": {
                "hostname_regex": "(.+)([a,b,A,B])(\\d)$",
                "variable_group_index": 1,
                "sequence": ["a", "b"]
            },
            'username': 'test_username',
            'password': 'test_password',
            'current_pdu': {
                'row': '04', 
                'rack': '07', 
                'pdu_letter': 'B', 
                'pdu_id': 'R04-07/B', 
                'pdu_hostname': 'ab-012345-ps-b1'
            }
        }
        mock_getpass.side_effect = ['test_password', 'test_password']
        mock_input.side_effect = ['', '', '', '', 'test_username', 'y']
        return_value = utils.prompt_utils.get_next_imd_config(config_to_update, False)
        self.assertEqual(config_to_update, expected_config)
        self.assertTrue(return_value)
    
    @mock.patch('utils.prompt_utils.input', create = True)
    @mock.patch('utils.prompt_utils.getpass', create = True)
    def test_get_next_imd_config_no_creds_current_pdu_guesses_next_cab(self, mock_getpass, mock_input):
        config_to_update = {
            'current_pdu': {
                'row': '04', 
                'rack': '07', 
                'pdu_letter': 'B', 
                'pdu_id': 'R04-07/B', 
                'pdu_hostname': 'ab-012345-ps-b1'
        }}
        expected_config = {
            'username': 'test_username',
            'password': 'test_password',
            'current_pdu': {
                'row': '04', 
                'rack': '08', 
                'pdu_letter': 'A', 
                'pdu_id': 'R04-08/A', 
                'pdu_hostname': 'ab-012346-ps-a1'
            }
        }
        mock_getpass.side_effect = ['test_password', 'test_password']
        mock_input.side_effect = ['', '', '', 'ab-012346-ps-a1', 'test_username', 'y']
        return_value = utils.prompt_utils.get_next_imd_config(config_to_update, False)
        self.assertEqual(config_to_update, expected_config)
        self.assertTrue(return_value)

    @mock.patch('utils.prompt_utils.input', create = True)
    @mock.patch('utils.prompt_utils.getpass', create = True)
    def test_get_next_imd_config_no_creds_current_pdu_guesses_next_try_again(self, mock_getpass, mock_input):
        config_to_update = {
            'current_pdu': {
                'row': '04', 
                'rack': '07', 
                'pdu_letter': 'B', 
                'pdu_id': 'R04-07/B', 
                'pdu_hostname': 'ab-012345-ps-b1'
        }}
        expected_config = {
            'username': 'test_username',
            'password': 'test_password',
            'current_pdu': {
                'row': '04', 
                'rack': '08', 
                'pdu_letter': 'A', 
                'pdu_id': 'R04-08/A', 
                'pdu_hostname': 'ab-012346-ps-a1'
            }
        }
        mock_getpass.side_effect = ['test_password', 'test_password', 'test_password', 'test_password']
        mock_input.side_effect = ['', '', '', 'ab-012346-ps-a1', 'test_username', 'n', 'y', 'y', 'test_username', '', '', '', 'ab-012346-ps-a1', 'y']
        return_value = utils.prompt_utils.get_next_imd_config(config_to_update, False)
        self.assertEqual(config_to_update, expected_config)
        self.assertTrue(return_value)

    @mock.patch('utils.prompt_utils.input', create = True)
    @mock.patch('utils.prompt_utils.getpass', create = True)
    def test_get_next_imd_config_give_up(self, mock_getpass, mock_input):
        config_to_update = {}
        expected_config = {
            'username': 'test_username',
            'password': 'test_password'
        }
        mock_getpass.side_effect = ['test_password', 'test_password']
        mock_input.side_effect = ['4', '7', 'b', 'ab-012345-ps-b1', 'test_username', 'n', 'n']
        return_value = utils.prompt_utils.get_next_imd_config(config_to_update, False)
        self.assertEqual(config_to_update, expected_config)
        self.assertFalse(return_value)