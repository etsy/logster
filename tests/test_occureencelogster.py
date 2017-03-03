from logster.parsers.OccurrenceLogster import OccurrenceLogster
import unittest, os, time

TEST_PATTERN_FILE = os.path.join(os.path.dirname(__file__), 'resources/patterns.txt')


class TestOccurrenceLogster(unittest.TestCase):

    def setUp(self):
        self.logster_raw = OccurrenceLogster("-p {} --raw".format(TEST_PATTERN_FILE))
        self.logster = OccurrenceLogster("-p {}".format(TEST_PATTERN_FILE))

    def test_valid_lines_raw(self):
        access_log_tmpl = "{} [%s], something goes in some way.".format(time.ctime())
        self.logster_raw.parse_line(access_log_tmpl % 'ERROR')
        self.logster_raw.parse_line(access_log_tmpl % 'error')
        self.logster_raw.parse_line(access_log_tmpl % 'WARN')
        self.assertEqual(2, self.logster_raw.error_type['errors'])
        self.assertEqual(3, self.logster_raw.error_type['hour_pattern'])
        self.assertEqual(2, len(self.logster_raw.error_type))

    def test_metrics_1sec_raw(self):
        self.test_valid_lines_raw()
        metrics = self.logster_raw.get_state(1)
        self.assertEqual(2, len(metrics))

        expected = {"errors": 2,
                    "hour_pattern": 3}
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_2sec_raw(self):
        self.test_valid_lines_raw()
        metrics = self.logster_raw.get_state(2)
        self.assertEqual(2, len(metrics))

        expected = {"errors": 2,
                    "hour_pattern": 3}
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_valid_lines(self):
        access_log_tmpl = "{} [%s], something goes in some way.".format(time.ctime())
        self.logster.parse_line(access_log_tmpl % 'ERROR')
        self.logster.parse_line(access_log_tmpl % 'error')
        self.logster.parse_line(access_log_tmpl % 'WARN')
        self.assertEqual(2, self.logster.error_type['errors'])
        self.assertEqual(3, self.logster.error_type['hour_pattern'])
        self.assertEqual(2, len(self.logster.error_type))

    def test_metrics_1sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(1)
        self.assertEqual(2, len(metrics))

        expected = {"errors": 2,
                    "hour_pattern": 3}
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

    def test_metrics_2sec(self):
        self.test_valid_lines()
        metrics = self.logster.get_state(2)
        self.assertEqual(2, len(metrics))

        expected = {"errors": 1.0,
                    "hour_pattern": 1.5}
        for m in metrics:
            self.assertEqual(expected[m.name], m.value)

if __name__ == '__main__':
    unittest.main()
