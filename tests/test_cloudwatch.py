from logster.logster_helper import MetricObject
from logster.outputs.cloudwatch import CloudWatch
from time import time, strftime, gmtime
import unittest

class TestCloudWatch(unittest.TestCase):

    def setUp(self):

        self.metric = MetricObject("ERROR", 1, None)
        self.metric.timestamp = strftime("%Y%m%dT%H:%M:00Z", gmtime(self.metric.timestamp))

        self.cw = CloudWatch("key", "secretkey", self.metric)
        self.cw.get_instance_id("myserverID").set_params().get_signed_url()

    def test_params(self):

        self.assertEqual(self.cw.base_url, "monitoring.ap-northeast-1.amazonaws.com")
        self.assertEqual(self.cw.key, "key")
        self.assertEqual(self.cw.secret_key, "secretkey")
        self.assertEqual(self.cw.url_params['Namespace'], "logster")
        self.assertEqual(self.cw.url_params['MetricData.member.1.MetricName'], "ERROR")
        self.assertEqual(self.cw.url_params['MetricData.member.1.Value'], 1)
        self.assertEqual(self.cw.url_params['MetricData.member.1.Unit'], None)
        self.assertEqual(self.cw.url_params['MetricData.member.1.Dimensions.member.1.Name'], "InstanceID")
        self.assertEqual(self.cw.url_params['MetricData.member.1.Dimensions.member.1.Value'], "myserverID")
        self.assertEqual(self.cw.url_params['AWSAccessKeyId'], "key")
        self.assertEqual(self.cw.url_params['Timestamp'], self.metric.timestamp)
        self.assertEqual(self.cw.url_params['Action'], 'PutMetricData')
        self.assertEqual(self.cw.url_params['SignatureMethod'], 'HmacSHA256')
        self.assertEqual(self.cw.url_params['SignatureVersion'], '2')
        self.assertEqual(self.cw.url_params['Version'], '2010-08-01')

if __name__ == '__main__':
    unittest.main()

