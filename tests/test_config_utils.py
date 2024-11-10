from unittest import TestCase

from utils.config_utils import get_config, get_prompt_with_default, get_credentials_from_imd_config
from utils.encryption_utils import decrypt

test_config: dict = {'encryption_iterations': 64}

class TestGetConfig(TestCase):

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    args = Namespace(imd_ip_address = None, config_file = 'default_config.json', prompts_file = 'default_prompts.json', spinner = 'shark')
    
    def test_get_config_returns_dict(self):
        self.assertEqual(type(get_config('./', self.args)), dict)
    
    def test_get_config_sets_default_ip(self):
        self.assertEqual(get_config('./', self.args)['current_imd_ip'], '192.168.123.123')


class TestGetPromptWithDefault(TestCase):

    def test_get_prompt_with_default_unique_value(self):
        unique_prompt_implicit: dict ={
            "config_item": "imd_hostname",
            "prompt_text": "",
            "default_value": "",
            "test": True}
    
        unique_prompt_explicit: dict ={
            "config_item": "imd_hostname",
            "unique_value": True,
            "prompt_text": "",
            "default_value": "",
            "test": True}
        
        returned_default_prompt_implicit = get_prompt_with_default(test_config, unique_prompt_implicit)
        returned_default_prompt_explicit = get_prompt_with_default(test_config, unique_prompt_explicit)
        self.assertEqual(returned_default_prompt_implicit, unique_prompt_implicit)
        self.assertEqual(returned_default_prompt_explicit, unique_prompt_explicit)
    
    def test_get_prompt_with_default_encrypted_non_unique_value(self):
        test_passphrase: str = 'test_passphrase'
        test_value: str = 'test_value'

        encrypted_non_unique_prompt: dict =  {
            "config_item": "primary_ntp",
            "unique_value": False,
            "encrypt_default": True,
            "salt": "",
            "default_value": "",
            "input_mode": "none",
            "test": True}

        returned_default_prompt = get_prompt_with_default(test_config, encrypted_non_unique_prompt, encryption_passphrase = test_passphrase, salt = b'', simulated_user_input = test_value)
        returned_default_value = returned_default_prompt['default_value']
        returned_salt = returned_default_prompt['salt']
        decrypted_default_value = decrypt(test_config, returned_salt, returned_default_value, test_passphrase)
        
        self.assertEqual(decrypted_default_value, test_value)


    def test_non_encrypted_non_unique_value(self):
        test_value: str = 'test_value'
        test_passphrase: str = 'test_passphrase'
        test_salt: bytes = b''
                
        non_encrypted_non_unique_prompt: dict = {
            "input_mode": "none",
            "unique_value": False,
            "encrypt_default": False,
            "default_value": "",
            "test": True}
        
        expected_prompt: dict = {
            "input_mode": "none",
            "unique_value": False,
            "encrypt_default": False,
            "default_value": test_value,
            "test": True}
        
        returned_default_prompt = get_prompt_with_default(test_config, non_encrypted_non_unique_prompt, encryption_passphrase = test_passphrase, salt = test_salt, simulated_user_input = test_value)
        self.assertDictEqual(returned_default_prompt, expected_prompt)

class TestGetCredentialsFromImdConfig(TestCase):
    def test_get_credentials_from_imd_config(self):
        test_imd_config = [{
            'config_item': 'credentials', 
            'api_calls': [{
                'cmd': 'add', 
                'method': 'post', 
                'api_path': 'auth', 
                'data': "{'username': 'test_username', 'password': 'test_password', 'enabled': 'true', 'contorol': 'true', 'admin': 'true'}"
            }]
        }]

        expected_credentials: tuple = ('test_username', 'test_password')
        returned_credentails = get_credentials_from_imd_config({}, test_imd_config)

        self.assertEqual(expected_credentials, returned_credentails)