from logster.logster_helper import LogsterOutput
from time import strftime, gmtime
import os
import sys
import base64
import hashlib
import hmac
import sys

try:
    from httplib import *
except ImportError:
    from http.client import *

try:
    from urllib import urlencode, quote_plus
except ImportError:
    from urllib.parse import urlencode, quote_plus


class CloudWatchException(Exception):
    """ Raise thie exception if the connection can't be established
        with Amazon server """
    pass


class CloudWatch(object):
    """ Base class for Amazon CloudWatch """
    def __init__(self, key, secret_key, metric):
        """ Specify Amazon CloudWatch params """

        self.base_url = "monitoring.ap-northeast-1.amazonaws.com"
        self.key = key
        self.secret_key = secret_key
        self.metric = metric

    def get_instance_id(self, instance_id = None):
        """ get instance id from amazon meta data server """

        self.instance_id = instance_id

        if self.instance_id is None:
            try:
                conn = HTTPConnection("169.254.169.254")
                conn.request("GET", "/latest/meta-data/instance-id")
            except Exception:
                raise CloudWatchException("Can't connect Amazon meta data server to get InstanceID : (%s)")

            self.instance_id = conn.getresponse().read()

        return self

    def set_params(self):

        params = {'Namespace': 'logster',
       'MetricData.member.1.MetricName': self.metric.name,
       'MetricData.member.1.Value': self.metric.value,
       'MetricData.member.1.Unit': self.metric.units,
       'MetricData.member.1.Dimensions.member.1.Name': 'InstanceID',
       'MetricData.member.1.Dimensions.member.1.Value': self.instance_id}

        self.url_params = params
        self.url_params['AWSAccessKeyId'] = self.key
        self.url_params['Action'] = 'PutMetricData'
        self.url_params['SignatureMethod'] = 'HmacSHA256'
        self.url_params['SignatureVersion'] = '2'
        self.url_params['Version'] = '2010-08-01'
        self.url_params['Timestamp'] = self.metric.timestamp

        return self

    def get_signed_url(self):
        """ build signed parameters following
            http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_PutMetricData.html """
        keys = sorted(self.url_params)
        values = map(self.url_params.get, keys)
        url_string = urlencode(list(zip(keys,values)))

        string_to_sign = "GET\n%s\n/\n%s" % (self.base_url, url_string)
        try:
            if sys.version_info[:2] == (2, 5):
                signature = hmac.new( key=self.secret_key, msg=string_to_sign, digestmod=hashlib.sha256).digest()
            else:
                signature = hmac.new( key=bytes(self.secret_key), msg=bytes(string_to_sign), digestmod=hashlib.sha256).digest()
        except TypeError:
            signature = hmac.new( key=self.secret_key.encode("utf-8"), msg=string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

        signature = base64.encodestring(signature).strip()
        urlencoded_signature = quote_plus(signature)
        url_string += "&Signature=%s" % urlencoded_signature

        return "/?" + url_string

    def put_data(self):
        signedURL = self.set_params().get_signed_url()
        try:
            conn = HTTPConnection(self.base_url)
            conn.request("GET", signedURL)
        except Exception:
            raise CloudWatchException("Can't connect Amazon CloudWatch server")
        res = conn.getresponse()


class CloudwatchOutput(LogsterOutput):
    shortname = 'cloudwatch'


    @classmethod
    def add_options(cls, parser):
        parser.add_option('--aws-key', action='store',
                          default=os.getenv('AWS_ACCESS_KEY_ID'), help='Amazon credential key')
        parser.add_option('--aws-secret-key', action='store',
                          default=os.getenv('AWS_SECRET_ACCESS_KEY_ID'), help='Amazon credential secret key')


    def __init__(self, parser, options, logger):
        super(CloudwatchOutput, self).__init__(parser, options, logger)
        if not options.aws_key or not options.aws_secret_key:
            parser.print_help()
            parser.error("You must supply --aws-key and --aws-secret-key or Set environment variables. AWS_ACCESS_KEY_ID for --aws-key, AWS_SECRET_ACCESS_KEY_ID for --aws-secret-key")
        self.aws_key = options.aws_key
        self.aws_secret_key = options.aws_secret_key


    def submit(self, metrics):
        for metric in metrics:
            metric_name = self.get_metric_name(metric)

            metric.timestamp = strftime("%Y%m%dT%H:%M:00Z", gmtime(metric.timestamp))
            metric.units = "None"
            metric_string = "%s %s %s" % (metric_name, metric.value, metric.timestamp)
            self.logger.debug("Submitting CloudWatch metric: %s" % metric_string)

            if (not self.dry_run):
                try:
                    cw = CloudWatch(self.aws_key, self.aws_secret_key, metric).get_instance_id()
                except CloudWatchException:
                    self.logger.debug("Is this machine really amazon EC2?")
                    sys.exit(1)

                try:
                    cw.put_data()
                except CloudWatchException as e:
                    self.logger.debug(e.message)
                    sys.exit(1)
            else:
                print(metric_string)

