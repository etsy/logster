from logster.parsers.SquidLogster import SquidLogster
from logster.logster_helper import LogsterParsingException
import unittest

class TestSquidLogster(unittest.TestCase):

    def setUp(self):
        self.logster = SquidLogster()

    def test_valid_lines(self):
        access_log_tmpl = '127.0.0.1 %s - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" %s/%s 2326'
        self.logster.parse_line(access_log_tmpl % (1, 'TCP_MISS', '200'))
        self.logster.parse_line(access_log_tmpl % (2, 'TCP_HIT', '201'))
        self.logster.parse_line(access_log_tmpl % (3, 'TCP_DENIED', '400'))
        self.logster.parse_line(access_log_tmpl % (4, 'NONE_TESTING', '504'))
        self.assertEqual(0, self.logster.http_1xx)
        self.assertEqual(2, self.logster.http_2xx)
        self.assertEqual(0, self.logster.http_3xx)
        self.assertEqual(1, self.logster.http_4xx)
        self.assertEqual(1, self.logster.http_5xx)
        self.assertEqual(1, self.logster.squid_codes['TCP_MISS'])
        self.assertEqual(1, self.logster.squid_codes['TCP_HIT'])
        self.assertEqual(1, self.logster.squid_codes['TCP_DENIED'])
        self.assertEqual(0, self.logster.squid_codes['TCP_MEM_HIT'])
        self.assertEqual(1, self.logster.squid_codes['OTHER'])
        self.assertEqual(10, self.logster.size_transferred)

    def test_metrics_1sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(1)
        self.assertEqual(11, len(metrics))

        expected = {"http_1xx": 0,
                    "http_2xx": 2,
                    "http_3xx": 0,
                    "http_4xx": 1,
                    "http_5xx": 1,
                    "size": 10,
                    "squid_TCP_MISS": 1,
                    "squid_TCP_HIT": 1,
                    "squid_TCP_DENIED": 1,
                    "squid_TCP_MEM_HIT": 0,
                    "squid_OTHER": 1,
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_2sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(2)
        self.assertEqual(11, len(metrics))

        expected = {"http_1xx": 0,
                    "http_2xx": 1,
                    "http_3xx": 0,
                    "http_4xx": 0.5,
                    "http_5xx": 0.5,
                    "size": 5,
                    "squid_TCP_MISS": 0.5,
                    "squid_TCP_HIT": 0.5,
                    "squid_TCP_DENIED": 0.5,
                    "squid_TCP_MEM_HIT": 0,
                    "squid_OTHER": 0.5,
                   }
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_invalid_line(self):
        self.assertRaises(LogsterParsingException, self.logster.parse_line, 'invalid log entry')

if __name__ == '__main__':
    unittest.main()

