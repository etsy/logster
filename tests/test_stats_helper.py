from logster.parsers import stats_helper
import unittest

class TestStatsHelper(unittest.TestCase):

    def test_median_of_1(self):
        self.assertEqual(stats_helper.find_median([0]), 0)
        self.assertEqual(stats_helper.find_median([1]), 1)
        self.assertEqual(stats_helper.find_median([1,2]), 1.5)
        self.assertEqual(stats_helper.find_median([1,2,3]), 2)
        self.assertEqual(stats_helper.find_median([1,-1]), 0)
        self.assertEqual(stats_helper.find_median([1,999999]), 500000)

    def test_median_floats(self):
        self.assertEqual(stats_helper.find_median([float(1.1),float(2.3),float(0.4)]), 1.1)

    def test_max_0(self):
        self.assertEqual(stats_helper.find_percentile([0],100), 0)
    def test_max_0_to_1(self):
        self.assertEqual(stats_helper.find_percentile([0,1],100), 1)
    def test_max_0_to_3(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3],100), 3)
    def test_max_0_to_5(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3,4,5],100), 5)
    def test_max_0_to_6(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3,4,5,6],100), 6)
    def test_max_0_to_10(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3,4,5,6,7,8,9,10],100), 10)
    def test_max_0_to_11(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3,4,5,6,7,8,9,10,11],100), 11)
    def test_max_floats(self):
        self.assertEqual(stats_helper.find_percentile([0,0.1,1.5,100],100), 100)

    def test_10th_0_to_10(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3,4,5,6,7,8,9,10],10), 1)

    def test_10th_1_to_3(self):
        self.assertEqual(stats_helper.find_percentile([1,2,3],10), 1.2)

    def test_12th_0_to_9(self):
        self.assertEqual(stats_helper.find_percentile([0,1,2,3,4,5,6,7,8,9],12), 1.08)

    def test_90th_0(self):
        self.assertEqual(stats_helper.find_percentile([0],90), 0)

    def test_90th_1(self):
        self.assertEqual(stats_helper.find_percentile([1],90), 1)

    def test_90th_1_2(self):
        self.assertEqual(stats_helper.find_percentile([1,2],90), 1.9)

    def test_90th_1_2_3(self):
        self.assertEqual(stats_helper.find_percentile([1,2,3],90), 2.8)

    def test_90th_1_minus1(self):
        self.assertEqual(stats_helper.find_percentile([1,-1],90), 0.8)

    def test_90th_1_to_10(self):
        self.assertEqual(stats_helper.find_percentile([1,2,3,4,5,6,7,8,9,10],90), 9.1)

    def test_90th_1_to_11(self):
        self.assertEqual(stats_helper.find_percentile([1,2,3,4,5,6,7,8,9,10,11],90), 10)

    def test_90th_1_to_15_noncontiguous(self):
        self.assertAlmostEqual(stats_helper.find_percentile([1,2,3,4,5,6,7,8,9,15],90), 9.6)
