# -*- coding: utf-8 -*-
###
###  AUTHOR: [duoduo369](https://github.com/duoduo369)
###
###  A logster parser file that can be used to count the number of different
###  messages in an Django error_log
###
###  For example:
###  sudo ./logster --dry-run --output=graphite --graphite-host=127.0.0.1:2003 DjangoLogster /var/log/your_django_log_file
###  log format -- [%(asctime)s] Level:%(levelname)s FuncName:%(funcName)s Line:%(lineno)d Message:%(message)s
###
###  if you use django, but log format is not like this, just modify MATCH_REG(re), to satisfy your requirement
###

import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class DjangoLogster(LogsterParser):

    MATCH_REG = r'^\[[^]]+\] Level:(?P<{level_key}>\w+) .*'
    LEVEL_KEY = 'level'
    LOG_LEVEL_MAPPER = {
        'NOTSET': 'notset',
        'DEBUG': 'debug',
        'INFO': 'info',
        'WARNING': 'warning',
        'ERROR': 'error',
        'CRITICAL': 'critical'
    }

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        for attr in self.LOG_LEVEL_MAPPER.itervalues():
            setattr(self, attr, 0)

        self.others = 0
        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line
        self.reg = re.compile(self.MATCH_REG.format(level_key=self.LEVEL_KEY))


    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                level = linebits[self.LEVEL_KEY]
                attr = self.LOG_LEVEL_MAPPER.get(level, 'others')
                setattr(self, attr, getattr(self, attr)+1)

            else:
                raise LogsterParsingException, "regmatch failed to match"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration / 10
        results = [MetricObject('django.OTHERS', self.others/self.duration, "Logs per 10 sec")]
        for level, attr in self.LOG_LEVEL_MAPPER.iteritems():
            results.append(MetricObject('django.{}'.format(level), (getattr(self, attr)/self.duration), "Logs per 10 sec"))
        return results
