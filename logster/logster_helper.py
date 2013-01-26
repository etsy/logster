#!/usr/bin/python

###
###  Copyright 2011, Etsy, Inc.
###
###  This file is part of Logster.
###  
###  Logster is free software: you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation, either version 3 of the License, or
###  (at your option) any later version.
###  
###  Logster is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
###  GNU General Public License for more details.
###  
###  You should have received a copy of the GNU General Public License
###  along with Logster. If not, see <http://www.gnu.org/licenses/>.
###

import httplib
import base64
import hashlib
import hmac

from urllib import urlencode, quote_plus
from time import time

class MetricObject(object):
    """General representation of a metric that can be used in many contexts"""
    def __init__(self, name, value, units='', type='float', timestamp=int(time())):
        self.name = name
        self.value = value
        self.units = units
        self.type = type
        self.timestamp = timestamp

class LogsterParser(object):
    """Base class for logster parsers"""
    def parse_line(self, line):
        """Take a line and do any parsing we need to do. Required for parsers"""
        raise RuntimeError, "Implement me!"

    def get_state(self, duration):
        """Run any calculations needed and return list of metric objects"""
        raise RuntimeError, "Implement me!"


class LogsterParsingException(Exception):
    """Raise this exception if the parse_line function wants to
        throw a 'recoverable' exception - i.e. you want parsing
        to continue but want to skip this line and log a failure."""
    pass

class LockingError(Exception):
    """ Exception raised for errors creating or destroying lockfiles. """
    pass

class CloudWatchException(Exception):
    """ Raise thie exception if the connection can't be established 
        with Amazon server """
    pass

class CloudWatch:
    """ Base class for Amazon CloudWatch """
    def __init__(self, key, secret_key, metric):
        """ Specify Amazon CloudWatch params """

        try:
            conn = httplib.HTTPConnection("169.254.169.254")
            conn.request("GET", "/latest/meta-data/instance-id")
        except Exception, e:
            raise CloudWatchException("Can't connect Amazon meta data server to get InstanceID : (%s)" % e.message)

        instance_id = conn.getresponse().read()

        self.base_url = "monitoring.ap-northeast-1.amazonaws.com"
        self.key = key
        self.secret_key = secret_key
        self.params = {'Namespace': 'logster',
       'MetricData.member.1.MetricName': metric.name,
       'MetricData.member.1.Value': metric.value,
       'MetricData.member.1.Unit': metric.units,
       'MetricData.member.1.Dimensions.member.1.Name': 'InstanceID',
       'MetricData.member.1.Dimensions.member.1.Value': instance_id}       
     
        self.url_params = self.params
        self.url_params['AWSAccessKeyId'] = self.key
        self.url_params['Action'] = 'PutMetricData'
        self.url_params['SignatureMethod'] = 'HmacSHA256'
        self.url_params['SignatureVersion'] = '2'
        self.url_params['Version'] = '2010-08-01'
        self.url_params['Timestamp'] = metric.timestamp
    
    def get_signed_url(self):
        """ build signed parameters following
            http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_PutMetricData.html """
        keys = self.url_params.keys()
        keys.sort()
        values = map(self.url_params.get, keys)
        url_string = urlencode(zip(keys,values))   

        string_to_sign = "GET\n%s\n/\n%s" % (self.base_url, url_string)
        signature = hmac.new( key=self.secret_key, msg=string_to_sign, digestmod=hashlib.sha256).digest()
        signature = base64.encodestring(signature).strip()
        urlencoded_signature = quote_plus(signature)
        url_string += "&Signature=%s" % urlencoded_signature

        return "/?" + url_string
 
    def put_data(self):
        signedURL = self.get_signed_url()
        try:
            conn = httplib.HTTPConnection(self.base_url)
            conn.request("GET", signedURL)
        except Exception, e:
            raise CloudWatchException("Can't connect Amazon CloudWatch server : (%s)" % e.message)
        res = conn.getresponse()


