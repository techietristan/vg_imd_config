from unittest import TestCase

from utils.spinner_utils import get_spinners_from_json_file, get_spinner

class TestGetSpinnersFromJsonFile(TestCase):
    def test_get_spinners_from_json_file_returns_dict(self):
        self.assertEqual(dict, type(get_spinners_from_json_file('spinners.json')))
    
    def test_get_spinners_from_json_file_returns_dict_with_multiple_keys(self):
        spinners: dict = get_spinners_from_json_file('spinners.json')
        spinner_names: list[str] = [ spinner_name for spinner_name in spinners.keys() ]
        print(type(spinner_names))
        self.assertTrue(len(spinner_names) > 1)

class TestGetSpinner(TestCase):

    def test_get_spinner_returns_dict(self):
        test_config: dict = {'spinner': 'arc'}
        self.assertEqual(dict, type(get_spinner(test_config)))
    
    def test_get_spinner_returns_correct_dict(self):
        test_config: dict = {'spinner': 'circle'}
        test_spinner: dict = {
            "interval": 120,
            "frames": ["◡", "⊙", "◠"]
        }

        self.assertDictEqual(get_spinner(test_config), test_spinner)
    
    def test_get_spinner_returns_correct_default(self):
        test_config: dict = {'spinner': 'not_a_valid_spinner'}
        test_default_spinner: dict = {
            "interval": 130,
            "frames": ["-", "\\", "|", "/"]
        }

        self.assertDictEqual(get_spinner(test_config), test_default_spinner)
    