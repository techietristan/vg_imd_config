from unittest import TestCase

from utils.time_utils import get_file_modification_time

class TestGetFileModificationTime(TestCase):
    def test_get_file_modification_time_returns_string(self):
        modification_time: str = get_file_modification_time(__file__)
        self.assertEqual(type(modification_time), str)
    
    def test_get_file_modification_time_returns_string_of_correct_length(self):
        modification_time: str = get_file_modification_time(__file__)
        year_month_day: str = modification_time.split(' ')[0]
        hour_minute_second: str = modification_time.split(' ')[1]
        self.assertEqual(len(hour_minute_second), 8)
        self.assertEqual(len(year_month_day), 10)
        self.assertEqual(len(modification_time), 19)