from logster.parsers.Log4jLogster import Log4jLogster
from logster.logster_helper import LogsterParsingException
import unittest

class TestLog4jLogster(unittest.TestCase):

    def setUp(self):
        self.logster = Log4jLogster()
        self.log_tmpl = '13:55:36 %s com.etsy.LogsterTest - This is a message'

    def test_valid_lines(self):
        self.logster.parse_line(self.log_tmpl % 'WARN')
        self.logster.parse_line(self.log_tmpl % 'ERROR')
        self.logster.parse_line(self.log_tmpl % 'ERROR')
        self.assertEqual(1, self.logster.WARN)
        self.assertEqual(2, self.logster.ERROR)
        self.assertEqual(0, self.logster.FATAL)

        self.assertRaises(LogsterParsingException, self.logster.parse_line, self.log_tmpl % 'DEBUG')
        self.assertFalse(hasattr(self.logster, 'DEBUG'))

    def test_valid_lines_non_default(self):
        debug_logster = Log4jLogster('--log-levels=DEBUG')
        debug_logster.parse_line(self.log_tmpl % 'DEBUG')
        self.assertEqual(1, debug_logster.DEBUG)

        self.assertRaises(LogsterParsingException, debug_logster.parse_line, self.log_tmpl % 'WARN')
        self.assertRaises(LogsterParsingException, debug_logster.parse_line, self.log_tmpl % 'ERROR')
        self.assertFalse(hasattr(debug_logster, 'WARN'))
        self.assertFalse(hasattr(debug_logster, 'ERROR'))
        self.assertFalse(hasattr(debug_logster, 'FATAL'))

    def test_metrics_1sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(1)
        self.assertEqual(3, len(metrics))

        expected = {"WARN": 1,
                    "ERROR": 2,
                    "FATAL": 0,
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_2sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(2)
        self.assertEqual(3, len(metrics))

        expected = {"WARN": 0.5,
                    "ERROR": 1,
                    "FATAL": 0,
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_invalid_line(self):
        self.assertRaises(LogsterParsingException, self.logster.parse_line, 'invalid log entry')

if __name__ == '__main__':
    unittest.main()

