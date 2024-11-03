from unittest import TestCase

from utils.format_utils import apply_formatting_function, apply_formatting_functions, format_user_input, get_value_to_display, get_formatted_config_items

class TestApplyFormattingFunction(TestCase):
    def test_apply_user_input_formatting_function_zfill(self):
        self.assertEqual('test', 'test')
        formatting_function_result = apply_formatting_function({}, ['zfill', 6], 'abc')
        self.assertEqual('000abc', formatting_function_result)
    def test_apply_user_input_formatting_function_lower(self):
        formatting_function_result = apply_formatting_function({}, ['upper'], 'test string')
        self.assertEqual('TEST STRING', formatting_function_result)
    def test_apply_user_input_formatting_function_upper(self):
        formatting_function_result = apply_formatting_function({}, ['lower'], 'TEST STRING')
        self.assertEqual('test string', formatting_function_result)

    test_string_formatter: dict = {
            "config-item": "location",
            "config-item-name": "Rack Location",
            "api_path": "conf/contact",
            "post_keys": ["description"],
            "format_functions": [[ "apply_string_template", "R{row}-{rack}/{pdu_letter}"]],
            "test": 0
    }

    test_string_parsed_promts: list[dict] = [
        {
            "config_item": "row",
            "value": "04",
        },
        {
            "config_item": "rack",
            "value": "04",
        },
        {
            "config_item": "pdu_letter",
            "value": "A",
        }
    ]

    expected_formatted_string: str = "R04-04/A"

    def test_apply_format_function_apply_string_template(self):
        format_function: list[str] = self.test_string_formatter['format_functions'][0]
        formatted_string = apply_formatting_function({}, format_function, '', self.test_string_parsed_promts)
        self.assertEqual(formatted_string, self.expected_formatted_string)

    test_json_formatter: dict = {
        "config-item": "ntp",
        "config-item-name": "NTP Servers",
        "cmd": "set",
        "format_functions": [[ "apply_string_template", "{{'ntpServer1': '{primary_ntp}', 'ntpServer2': '{secondary_ntp}'}}"]],
        "api_calls": [
            {
                "method":   "post",
                "api_path": "conf/contact/",
            }
        ]
    }
    
    test_json_parsed_promt_responses: list[dict] = [
        {
            "config_item": "primary_ntp",
            "value": "test.primary_ntp.net",
        },
        {
            "config_item": "secondary_ntp",
            "value": "test.secondary_ntp.net",
        },
    ]

    expected_formatted_json: str = "{'ntpServer1': 'test.primary_ntp.net', 'ntpServer2': 'test.secondary_ntp.net'}"

    def test_apply_format_function_json(self):
        format_function: list = self.test_json_formatter['format_functions'][0]
        formatted_json = apply_formatting_function({}, format_function, '', self.test_json_parsed_promt_responses)

class TestApplyFormattingFunctions(TestCase):
    def test_apply_format_functions_json(self):
        test_string_formatter: dict = {
                "config-item": "location",
                "config-item-name": "Rack Location",
                "api_path": "conf/contact",
                "post_keys": ["description"],
                "format_functions": [[ "apply_string_template", "R{row}-{rack}/{pdu_letter}"],["upper"]],
                "test": 0
        }

        test_string_parsed_promts: list[dict] = [
            {
                "config_item": "row",
                "value": "07",
            },
            {
                "config_item": "rack",
                "value": "09",
            },
            {
                "config_item": "pdu_letter",
                "value": "b",
            }
        ]

        expected_formatted_string: str = "R07-09/B"

        format_functions: list[list] = test_string_formatter['format_functions']
        formatted_string = apply_formatting_functions({}, format_functions, '', test_string_parsed_promts)
        self.assertEqual(expected_formatted_string, formatted_string)



class TestFormatUserInput(TestCase):
    def test_format_user_input_none(self):
        test_prompt = {'format_functions': [[]], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'test_input ')
        self.assertEqual(formatted_user_input, 'test_input')
    def test_format_user_input_zfill(self):
        test_prompt = {'format_functions': [['zfill', 2]], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, '7 ')
        self.assertEqual(formatted_user_input, '07')
    def test_format_user_input_lower(self):
        test_prompt = {'format_functions': [['lower']], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'TEST INPUT ')
        self.assertEqual(formatted_user_input, 'test input')
    def test_format_user_input_upper(self):
        test_prompt = {'format_functions': [['upper']], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'test input ')
        self.assertEqual(formatted_user_input, 'TEST INPUT')
    def test_format_user_input_zfill_upper(self):
        test_prompt = {'format_functions': [['zfill', 6], ['upper']], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'abc ')
        self.assertEqual(formatted_user_input, '000ABC')
    def test_format_user_input_zfill_lower(self):
        test_prompt = {'format_functions': [['zfill', 6], ['lower']], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, ' ABC')
        self.assertEqual(formatted_user_input, '000abc')  
    def test_format_user_input_upper_zfill(self):
        test_prompt = {'format_functions': [['upper'], ['zfill', 6]], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, 'abc ')
        self.assertEqual(formatted_user_input, '000ABC')
    def test_format_user_input_lower_zfill(self):
        test_prompt = {'format_functions': [['lower'], ['zfill', 6]], 'empty_allowed': 0}
        formatted_user_input = format_user_input({}, test_prompt, ' ABC')
        self.assertEqual(formatted_user_input, '000abc')  

class TestGetFormattedConfigItems(TestCase):
    def test_get_formatted_config_items(self):
        test_config_items: list[dict] = [
        {
            "config_item": 'primary_ntp',
            "config_item_name": "Primary NTP",
            "value": 'test.primary_ntp.net',
            "test": 1
        },
        {
            "config_item": 'secondary_ntp',
            "config_item_name": "Secondary NTP",
            "value": 'test.secondary_ntp.net',
            "test": 1
        },        
    ]
        test_prompts: dict = {
        "formatters": [
            {
                "config_item": "ntp",
                "config_item_name": "NTP Servers",
                "format_functions": [[ "apply_string_template", "{{'ntpServer1': '{primary_ntp}', 'ntpServer2': '{secondary_ntp}'}}"]],
                "display_to_user": 1,
                "value_to_display": "{primary_ntp}, {secondary_ntp}",
                "api_calls": [
                    {
                        "cmd":      "set",
                        "method":   "post",
                        "api_path": "conf/contact"
                    }
                ]
            },
        ]}

        expected_config_items: list[dict] = [{
                "config_item": "ntp",
                "config_item_name": "NTP Servers",
                "display_to_user": 1,
                "value_to_display": "test.primary_ntp.net, test.secondary_ntp.net",
                "api_calls": [
                    {
                        "cmd":      "set",
                        "method":   "post",
                        "api_path": "conf/contact",
                        "data": "{'ntpServer1': 'test.primary_ntp.net', 'ntpServer2': 'test.secondary_ntp.net'}"
                    }
                ]
        }]
        returned_config_items = get_formatted_config_items({}, test_prompts, test_config_items)
        self.assertDictEqual(expected_config_items[0], returned_config_items[0])
    
class TestGetValueToDisplay(TestCase):
    def test_get_value_to_display(self):
        test_config: dict = {}
        test_formatter: dict ={
            "value_to_display": "{primary_ntp}, {secondary_ntp}",
        }
        test_config_items: list[dict] = [
            {
                "config_item": 'primary_ntp',
                "config_item_name": "Primary NTP",
                "value": 'test.primary_ntp.net',
                "test": 1
            },
            {
                "config_item": 'secondary_ntp',
                "config_item_name": "Secondary NTP",
                "value": 'test.secondary_ntp.net',
                "test": 1
            },        
        ] 
        expected_value_to_return: str = "test.primary_ntp.net, test.secondary_ntp.net"
        returned_value: str | None = get_value_to_display(test_config, test_formatter, test_config_items)
        returned_value_missing_config_items: str | None = get_value_to_display(test_config, test_formatter, {})
        self.assertEqual(expected_value_to_return, returned_value)
        self.assertEqual(None, returned_value_missing_config_items)

