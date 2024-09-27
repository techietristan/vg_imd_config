import unittest

from utils.config_utils import get_config

class TestGetConfig(unittest.TestCase):

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    args = Namespace(imd_ip_address = None, config_file = 'default_config.json', prompts_file = 'default_prompts.json')
    
    def test_get_config_returns_dict(self):
        self.assertEqual(type(get_config('./', self.args)), dict)
    
    def test_get_config_sets_default_ip(self):
        self.assertEqual(get_config('./', self.args)['current_imd_ip'], '192.168.123.123')