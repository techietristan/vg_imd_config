import unittest

from utils.config_utils import get_config, get_prompt_default
from utils.encryption_utils import encrypt, decrypt

class TestGetConfig(unittest.TestCase):

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    args = Namespace(imd_ip_address = None, config_file = 'default_config.json', prompts_file = 'default_prompts.json')
    
    def test_get_config_returns_dict(self):
        self.assertEqual(type(get_config('./', self.args)), dict)
    
    def test_get_config_sets_default_ip(self):
        self.assertEqual(get_config('./', self.args)['current_imd_ip'], '192.168.123.123')


class TestGetPromptDefault(unittest.TestCase):

    test_config: dict = {"encryption_iterations": 32}

    def test_get_prompt_default_unique_value(self):
        unique_prompt: dict ={
            "config_item": "imd_hostname",
            "default_value": "",
            "test": 1}
        
        returned_default_prompt = get_prompt_default(self.test_config, unique_prompt)
        self.assertEqual(returned_default_prompt, unique_prompt)
    
    def test_get_prompt_default_encrypted_non_unique_value(self):
        test_passphrase: str = 'test_passphrase'
        test_value: str = 'test_value'
        salt, encrypted_value = encrypt(self.test_config, test_passphrase, test_value)

        encrypted_non_unique_prompt: dict =  {
            "config_item": "primary_ntp",
            "unique_value": 0,
            "encrypt_default": 1,
            "salt": "",
            "default_value": "",
            "test": 1}

        expected_prompt: dict ={
            "config_item": "primary_ntp",
            "unique_value": 0,
            "encrypt_default": 1,
            "salt": salt,
            "default_value": encrypted_value,
            "test": 1}
        
        returned_default_prompt = get_prompt_default(self.test_config, encrypted_non_unique_prompt, test_value)
        self.assertDictEqual(returned_default_prompt, expected_prompt)

    def test_non_encrypted_non_unique_value(self):
        test_value: str = 'test_value'
                
        non_encrypted_non_unique_prompt: dict = {
            "unique_value": 0,
            "encrypt_default": 0,
            "default_value": "",
            "test": 1}
        
        expected_prompt: dict = {
            "unique_value": 0,
            "encrypt_default": 0,
            "default_value": test_value,
            "test": 1}
        
        returned_default_prompt = get_prompt_default(self.test_config, non_encrypted_non_unique_prompt, test_value)
        self.assertDictEqual(returned_default_prompt, expected_prompt)