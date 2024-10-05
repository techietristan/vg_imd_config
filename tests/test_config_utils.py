import unittest

from utils.config_utils import get_config, get_prompt_with_default
from utils.encryption_utils import encrypt, decrypt

test_config: dict = {'encryption_iterations': 64}

class TestGetConfig(unittest.TestCase):

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    args = Namespace(imd_ip_address = None, config_file = 'default_config.json', prompts_file = 'default_prompts.json')
    
    def test_get_config_returns_dict(self):
        self.assertEqual(type(get_config('./', self.args)), dict)
    
    def test_get_config_sets_default_ip(self):
        self.assertEqual(get_config('./', self.args)['current_imd_ip'], '192.168.123.123')


class TestGetPromptWithDefault(unittest.TestCase):

    def test_get_prompt_with_default_unique_value(self):
        unique_prompt_implicit: dict ={
            "config_item": "imd_hostname",
            "prompt_text": "",
            "default_value": "",
            "test": 1}
    
        unique_prompt_explicit: dict ={
            "config_item": "imd_hostname",
            "unique_value": 1,
            "prompt_text": "",
            "default_value": "",
            "test": 1}
        
        returned_default_prompt_implicit = get_prompt_with_default(test_config, unique_prompt_implicit)
        returned_default_prompt_explicit = get_prompt_with_default(test_config, unique_prompt_explicit)
        self.assertEqual(returned_default_prompt_implicit, unique_prompt_implicit)
        self.assertEqual(returned_default_prompt_explicit, unique_prompt_explicit)
    
    def test_get_prompt_with_default_encrypted_non_unique_value(self):
        test_passphrase: str = 'test_passphrase'
        test_value: str = 'test_value'

        encrypted_non_unique_prompt: dict =  {
            "config_item": "primary_ntp",
            "unique_value": 0,
            "encrypt_default": 1,
            "salt": "",
            "default_value": "",
            "input_mode": "none",
            "test": 1}

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
            "unique_value": 0,
            "encrypt_default": 0,
            "default_value": "",
            "test": 1}
        
        expected_prompt: dict = {
            "input_mode": "none",
            "unique_value": 0,
            "encrypt_default": 0,
            "default_value": test_value,
            "test": 1}
        
        returned_default_prompt = get_prompt_with_default(test_config, non_encrypted_non_unique_prompt, encryption_passphrase = test_passphrase, salt = test_salt, simulated_user_input = test_value)
        self.assertDictEqual(returned_default_prompt, expected_prompt)