from unittest import TestCase
from utils.api_utils import get_ordered_api_calls
from utils.format_utils import format_red

class TestGetOrderedApiCalls(TestCase):

    test_config: dict = {}
    
    test_prompts: dict = {
        "version": "0.1",
        "greeting": {
            "text": "\nWelcome to the Vertiv Geist IMD Configuration Script!\n",
            "display": 1
        },

        "formatters": [
            {
                "config_item": "label",
                "config_item_name": "Hostname Label",
                "format_functions": [[ "apply_string_template", "{{'label': '{imd_hostname}', 'hostname': '{imd_hostname}' }}"]],
                "display_to_user": 1,
                "value_to_display": "{imd_hostname}",
                "api_calls": [
                    {
                        "cmd":      "set",
                        "method":   "post",
                        "api_path": "system"
                    }
                ]
            },
            {
                "config_item": "ntp",
                "config_item_name": "NTP Servers",
                "format_functions": [[ "apply_string_template", "{{'ntpServer1': '{primary_ntp}', 'ntpServer2': '{secondary_ntp}'}}"]],
                "api_calls": [
                    {
                        "cmd":      "set",
                        "method":   "post",
                        "api_path": "conf/contact"
                    }
                ]
            },
        ],

        "defaults": [
            {
                "config_item": "ipv6",
                "config_item_name": "IPv6",
                "api_calls": [
                    {
                        "method":   "post",
                        "api_path": "system",
                        "cmd":      "set",
                        "data":     {"ip6Enabled": "false"}
                    }
                ]
            }
        ],

        "api_call_sequence": [
            "label",
            "ipv6",
            "ntp",
        ]
    }

    test_config_items: list[dict] = [
        {
            "config_item": "imd_hostname",
            "value": 'test_hostname',
            "test": 1
        },
        {
            "config_item": "primary_ntp",
            "value": 'test.primary_ntp.net',
            "test": 1
        },
        {
            "config_item": "secondary_ntp",
            "value": 'test.secondary_ntp.net',
            "test": 1            
        }
    ]

    expected_ordered_api_calls: list[dict] = [
        {'config_item': 'label', 'config_item_name': 'Hostname Label', 'display_to_user': True, 'value_to_display': 'test_hostname', 'api_calls': [{'cmd': 'set', 'method': 'post', 'api_path': 'system', 'data': "{'label': 'test_hostname', 'hostname': 'test_hostname' }"}]}, 
        {'config_item': 'ipv6', 'config_item_name': 'IPv6', 'api_calls': [{'method': 'post', 'api_path': 'system', 'cmd': 'set', 'data': {'ip6Enabled': 'false'}}]}, 
        {'config_item': 'ntp', 'config_item_name': 'NTP Servers', 'display_to_user': False, 'value_to_display': None, 'api_calls': [{'cmd': 'set', 'method': 'post', 'api_path': 'conf/contact', 'data': "{'ntpServer1': 'test.primary_ntp.net', 'ntpServer2': 'test.secondary_ntp.net'}"}]}
    ]

    def test_get_ordered_api_calls(self):
        returned_ordered_api_calls: list[dict] = get_ordered_api_calls(self.test_config, self.test_prompts, self.test_config_items)
        for index, api_call in enumerate(self.expected_ordered_api_calls):
            self.assertDictEqual(api_call, returned_ordered_api_calls[index])