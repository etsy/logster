from logster.parsers.ErrorLogLogster import ErrorLogLogster
from logster.logster_helper import LogsterParsingException
import unittest

class TestErrorLogLogster(unittest.TestCase):

    def setUp(self):
        self.logster = ErrorLogLogster()

    def test_valid_lines(self):
        error_log_tmpl = '[Wed Oct 11 14:32:52 2000] [%s] [client 127.0.0.1] client denied by server configuration: /export/home/live/ap/htdocs/test'
        self.logster.parse_line(error_log_tmpl % 'error')
        self.logster.parse_line(error_log_tmpl % 'error')
        self.logster.parse_line(error_log_tmpl % 'notice')
        self.logster.parse_line(error_log_tmpl % 'other')

        self.assertEqual(1, self.logster.notice)
        self.assertEqual(0, self.logster.warn)
        self.assertEqual(2, self.logster.error)
        self.assertEqual(0, self.logster.crit)
        self.assertEqual(1, self.logster.other)

    def test_metrics_1sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(1)
        self.assertEqual(5, len(metrics))

        expected = {"notice": 10,
                    "warn": 0,
                    "error": 20,
                    "crit": 0,
                    "other": 10
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_2sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(2)
        self.assertEqual(5, len(metrics))

        expected = {"notice": 5,
                    "warn": 0,
                    "error": 10,
                    "crit": 0,
                    "other": 5
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_invalid_line(self):
        self.assertRaises(LogsterParsingException, self.logster.parse_line, 'invalid log entry')

if __name__ == '__main__':
    unittest.main()

