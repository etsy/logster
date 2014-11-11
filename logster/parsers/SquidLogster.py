###  A sample logster parser file that can be used to count the number
###  of responses and object size in the squid access.log
###
###  For example:
###  sudo ./logster --dry-run --output=ganglia SquidLogster /var/log/squid/access.log
###
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

import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class SquidLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.size_transferred = 0
        self.squid_codes = {
                'TCP_MISS': 0,
                'TCP_DENIED': 0,
                'TCP_HIT': 0,
                'TCP_MEM_HIT': 0,
                'OTHER': 0,
                }
        self.http_1xx = 0
        self.http_2xx = 0
        self.http_3xx = 0
        self.http_4xx = 0
        self.http_5xx = 0

        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, http_status_code, size and squid_code).
        self.reg = re.compile('^[0-9.]+ +(?P<size>[0-9]+) .*(?P<squid_code>(TCP|UDP|NONE)_[A-Z_]+)/(?P<http_status_code>\d{3}) .*')


    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                status = int(linebits['http_status_code'])
                squid_code = linebits['squid_code']
                size = int(linebits['size'])

                if (status < 200):
                    self.http_1xx += 1
                elif (status < 300):
                    self.http_2xx += 1
                elif (status < 400):
                    self.http_3xx += 1
                elif (status < 500):
                    self.http_4xx += 1
                else:
                    self.http_5xx += 1

                if squid_code in self.squid_codes:
                    self.squid_codes[squid_code] += 1
                else:
                    self.squid_codes['OTHER'] += 1

                self.size_transferred += size

            else:
                raise LogsterParsingException("regmatch failed to match")

        except Exception as e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = float(duration)

        # Return a list of metrics objects
        return_array = [
            MetricObject("http_1xx", (self.http_1xx / self.duration), "Responses per sec"),
            MetricObject("http_2xx", (self.http_2xx / self.duration), "Responses per sec"),
            MetricObject("http_3xx", (self.http_3xx / self.duration), "Responses per sec"),
            MetricObject("http_4xx", (self.http_4xx / self.duration), "Responses per sec"),
            MetricObject("http_5xx", (self.http_5xx / self.duration), "Responses per sec"),
            MetricObject("size", (self.size_transferred / self.duration), "Size per sec")
        ]
        for squid_code in self.squid_codes:
            return_array.append(MetricObject("squid_" + squid_code, (self.squid_codes[squid_code]/self.duration), "Squid code per sec"))

        return return_array
