from unittest import TestCase

from utils.dict_utils import get_value_if_key_exists

test_dict: dict = {'key1': 'value1', 'key3': 'value3'}
test_valid_key: str = 'key3'
test_valid_value: str = 'value3'
test_missing_key: str = 'key2'

class TestGetValueIfKeyExists(TestCase):

    def test_get_value_if_key_exists_returns_false_if_key_missing(self):
        self.assertFalse(get_value_if_key_exists(test_dict, test_missing_key))
    
    def test_get_value_if_key_exists_returns_value_if_key_exists(self):
        test_value = get_value_if_key_exists(test_dict, test_valid_key)
        self.assertEqual(test_value, test_valid_value)

