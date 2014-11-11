###  Author: Mike Babineau <michael.babineau@gmail.com>, EA2D <http://ea2d.com>
###
###  A sample logster parser file that can be used to count the number
###  of events for each log level in a log4j log.
###
###  Example (note WARN,ERROR,FATAL is default):
###  sudo ./logster --output=stdout Log4jLogster /var/log/example_app/app.log --parser-options '-l WARN,ERROR,FATAL'
###
###
###  Logster copyright 2011, Etsy, Inc.
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
import optparse

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class Log4jLogster(LogsterParser):
    
    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        
        if option_string:
            options = option_string.split(' ')
        else:
            options = []
        
        optparser = optparse.OptionParser()
        optparser.add_option('--log-levels', '-l', dest='levels', default='WARN,ERROR,FATAL',
                            help='Comma-separated list of log levels to track: (default: "WARN,ERROR,FATAL")')
        
        opts, args = optparser.parse_args(args=options)
            
        self.levels = opts.levels.split(',')
        
        for level in self.levels:
            # Track counts from 0 for each log level
            setattr(self, level, 0)
        
        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, a log level such as WARN, ERROR, or FATAL).
        self.reg = re.compile('[0-9-_:\.]+ (?P<log_level>%s)' % ('|'.join(self.levels)) )
        
        
    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''
        
        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)
            
            if regMatch:
                linebits = regMatch.groupdict()
                log_level = linebits['log_level']
                
                if log_level in self.levels:
                    current_val = getattr(self, log_level)
                    setattr(self, log_level, current_val+1)
                    
            else:
                raise LogsterParsingException("regmatch failed to match")
                
        except Exception as e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)
            
            
    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = float(duration)
        
        metrics = [MetricObject(level, (getattr(self, level) / self.duration)) for level in self.levels]
        return metrics
