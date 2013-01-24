import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class DnsmasqLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        
        self.replies = 0
        self.forwards = 0
        self.cache_hits = 0
        self.queries = 0
        

        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, http_status_code).
        self.reg = re.compile('.*dnsmasq\[[0-9]+\]:\s(?P<dnsmasq_event_type>[a-z]+)\[?(?P<query_type>[A-Z]+)?\]?\s.*')
        # pretty nasty regex made nastier to cleanly extract the query type
        # example log lines:
        # Jan 22 14:26:44 dnsmasq[31180]: query[AAAA] ec2-127-0-0-1.compute-1.amazonaws.com from 192.168.1.1
        # cached ec2-127-0-0-1.compute-1.amazonaws.com is 127.0.0.1

    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                event_type = linebits['dnsmasq_event_type']

                if event_type == 'reply':
                    self.replies += 1
                elif event_type == 'forwarded':
                    self.forwards += 1
                elif event_type == 'cached':
                    self.cache_hits += 1
                elif event_type == 'query':
                    self.queries += 1

            else:
                raise LogsterParsingException, "regmatch failed to match"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = duration

        # Return a list of metrics objects
        return [
            MetricObject("replies", (self.replies / self.duration), "Replies PS"),
            MetricObject("forwards", (self.forwards / self.duration), "Forwards PS"),
            MetricObject("cache_hits", (self.cache_hits / self.duration), "Cache hits PS"),
            MetricObject("queries", (self.queries / self.duration), "Queries PS"),
        ]
