###  A logster parser file that can be used to count the number of different
###  messages in an Apache error_log
###
###  For example:
###  sudo ./logster --dry-run --output=ganglia ErrorLogLogster /var/log/httpd/error_log
###
###

import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class ErrorLogLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.notice = 0
        self.warn = 0
        self.error = 0
        self.crit = 0
        self.other = 0
        
        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line
        self.reg = re.compile('^\[[^]]+\] \[(?P<loglevel>\w+)\] .*')


    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                level = linebits['loglevel']

                if (level == 'notice'):
                    self.notice += 1
                elif (level == 'warn'):
                    self.warn += 1
                elif (level == 'error'):
                    self.error += 1
                elif (level == 'crit'):
                    self.crit += 1
                else:
                    self.other += 1

            else:
                raise LogsterParsingException("regmatch failed to match")

        except Exception as e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration / 10.0

        # Return a list of metrics objects
        return [
            MetricObject("notice", (self.notice / self.duration), "Logs per 10 sec"),
            MetricObject("warn", (self.warn / self.duration), "Logs per 10 sec"),
            MetricObject("error", (self.error / self.duration), "Logs per 10 sec"),
            MetricObject("crit", (self.crit / self.duration), "Logs per 10 sec"),
            MetricObject("other", (self.other / self.duration), "Logs per 10 sec"),
        ]
