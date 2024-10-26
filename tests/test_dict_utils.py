from unittest import TestCase

from utils.dict_utils import get_dict_with_matching_key_value_pair, get_value_if_key_exists

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

class TestGetDictWithMatchingKeyValuePair(TestCase):

    test_dicts: list[dict] = [
        {'key1': 'value1'},
        {'key2': 'value2'},
        {'key3': 'value3'}
    ]

    def test_get_dict_with_matching_key_value_pair(self):
        self.assertEqual(self.test_dicts[1], get_dict_with_matching_key_value_pair(self.test_dicts, 'key2', 'value2'))

    def test_get_dict_with_matching_key_value_pair_returns_none_if_no_match(self):
        self.assertEqual({}, get_dict_with_matching_key_value_pair(self.test_dicts, 'key4', 'value4'))