import unittest

import logster.run

class TestStatsHelper(unittest.TestCase):

    def test_load_parser_simple_name(self):
        """
        Load the ErrorLogLogster using just the name
        """
        parser = logster.run.load_parser('ErrorLogLogster')
        self.assertEqual(parser.__class__.__name__, 'ErrorLogLogster')

    def test_load_parser_with_module(self):
        """
        Load the ErrorLogLogster using the full module path
        """
        parser = logster.run.load_parser(
            'logster.parsers.ErrorLogLogster:ErrorLogLogster')
        self.assertEqual(parser.__class__.__name__, 'ErrorLogLogster')

    def test_load_parser_with_parameters(self):
        """
        Load the MetricLogster passing parameters
        """
        parser = logster.run.load_parser('MetricLogster',
            option_string='--percentiles 40,50')
        self.assertEqual(parser.percentiles, ['40', '50'])
