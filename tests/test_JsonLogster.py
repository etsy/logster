from logster.parsers.JsonLogster import JsonLogster
from logster.logster_helper import LogsterParsingException
import unittest

class TestJsonLogster(unittest.TestCase):
    def setUp(self):
        self.json_line = '{     "1.1": {         "value1": 0,         "value2": "hi",         "1.2": {             "value3": 0.1,             "value4": false         }     },     "2.1": ["a","b"] }'
        self.json_data = {
            '1.1': {
                'value1': 0,
                'value2': 'hi',
                '1.2': {
                    'value3': 0.1,
                    'value4': False,
                }
            },
            '2.1': ['a','b'],
        }
        self.key_separator = '&'
        self.flattened_should_be = {
            '1.1&value1': 0,
            '1.1&valuetwo': 'hi',
            '1.1&1.2&value3': 0.1,
            '1.1&1.2&value4': False,
            '2.1&0': 'a',
            '2.1&1': 'b',
        }

        self.json_logster = JsonLogster('--key-separator ' + self.key_separator)

    def key_filter_callback(self, key):
        if key == 'value2':
            key = 'valuetwo'

        return key

    def test_init(self):
        self.assertEqual(self.json_logster.key_separator, self.key_separator)

    def test_flatten_object(self):
        flattened = self.json_logster.flatten_object(self.json_data, self.key_separator, self.key_filter_callback)
        self.assertEqual(flattened, self.flattened_should_be)

    def test_invalid_json(self):
        self.assertRaises(LogsterParsingException, self.json_logster.parse_line, '{ "hello": "world"')


if __name__ == '__main__':
    unittest.main()
