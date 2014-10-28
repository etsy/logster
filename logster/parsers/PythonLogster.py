# -*- coding: utf-8 -*-
###
###  AUTHOR: [duoduo369](https://github.com/duoduo369)
###
###  A logster parser file that can be used to count the number of different
###  messages in an Python error_log
###
###  For example:
###  sudo ./logster --dry-run --output=graphite --graphite-host=127.0.0.1:2003 PythonLogster /var/log/your_python_log_file
###  log format -- [%(asctime)s] Level:%(levelname)s FuncName:%(funcName)s Line:%(lineno)d Message:%(message)s
###
###  if you use python or django or some other python project,
###  just modify MATCH_REG(re), to satisfy your log format.
###

import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class PythonLogster(LogsterParser):

    MATCH_REG = r'^\[[^]]+\] Level:(?P<{level_key}>\w+) .*'
    LEVEL_KEY = 'level'
    METRIC_PREFIX = 'python.profix'
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
            reg_match = self.reg.match(line)

            if reg_match:
                linebits = reg_match.groupdict()
                level = linebits[self.LEVEL_KEY]
                attr = self.LOG_LEVEL_MAPPER.get(level, 'others')
                setattr(self, attr, getattr(self, attr)+1)

            else:
                raise LogsterParsingException("regmatch failed to match")

        except Exception, ex:
            raise LogsterParsingException("regmatch or contents failed with {}".format(ex))


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        duration = duration / 10
        results = [MetricObject('{}.OTHERS'.format(self.METRIC_PREFIX), self.others/duration, "Logs per 10 sec")]
        for level, attr in self.LOG_LEVEL_MAPPER.iteritems():
            results.append(MetricObject('{}.{}'.format(self.METRIC_PREFIX, level), (getattr(self, attr)/duration), "Logs per 10 sec"))
        return results
