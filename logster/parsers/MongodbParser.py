###  logster parser file that collects various metrics, slow query counts
###  from mongodb logs
###
###  For example:
###  sudo logster --dry-run --output=graphite --graphite-host=localhost:2003 MongodbParser /var/log/mongodb/mongodb.log
import time
import re
from collections import defaultdict
from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class MongodbParser(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.authentication = 0
        self.connection_accepted = 0
        self.assertion_exception = 0
        self.exception_count = 0
        self.reg = re.compile('.*')
        self.slow_query_req = re.compile('.*ms$')
        self.slow_query_count = 0
        self.slow = defaultdict(list)


    def parse_line(self, line):
        try:
            # Apply regular expression to each line and extract interesting bits.
            if "authenticate" in line:
                self.authentication += 1
            elif "connection accepted" in line:
                self.connection_accepted += 1
            elif "AssertionException" in line:
                self.assertion_exception += 1
            elif "Exception" in line:
                self.exception_count += 1
            elif self.slow_query_req.match(line):
                self.slow_query_count += 1
                # Mon Feb 10 07:12:48.549 [conn5] query blog.articles query: { $query: {}, $orderby: { created_at: -1 } } ntoreturn:10 ntoskip:0 nscanned:99999 scanAndOrder:1 keyUpdates:0 numYields: 1 locks(micros) r:1696987 nreturned:10 reslen:14581 1265ms
                # Mon Feb 10 07:12:49.750 [conn5] query blog.users query: { $query: {}, $orderby: { created_at: -1 } } ntoreturn:10 ntoskip:0 nscanned:99999 scanAndOrder:1 keyUpdates:0 numYields: 1 locks(micros) r:1366296 nreturned:10 reslen:13050 1182ms
                r = re.match(".*\[conn.*\] (.*?) (.*?)\.(.*?) .* (.*)ms$", line)
                if r:
                    op, db, coll, t = r.groups()
                    self.slow["%s.%s.%s" % (db, coll, op)].append(int(t))
        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        self.duration = duration

        # Return a list of metrics objects
        ret = [
            MetricObject("mongodb.connection_accepted", self.connection_accepted, "connection_accepted per sec"),
            MetricObject("mongodb.authentication_per_sec", (self.authentication / self.duration), "authentication per sec"),
            MetricObject("mongodb.authentication", self.authentication, "authentication"),
            MetricObject("mongodb.assertion_exception", self.assertion_exception, "assertion_exception per sec"),
            MetricObject("mongodb.slow_query_count", self.slow_query_count, "assertion_exception per sec"),
        ]

        for k, v in self.slow.iteritems():
            value = len(v)
            average = sum(v) / float(len(v))
            ret.append(MetricObject("mongodb.%s.count" % k, value, "slow query breakdown"))
            ret.append(MetricObject("mongodb.%s.max" % k, max(v), "slow query breakdown"))
            ret.append(MetricObject("mongodb.%s.min" % k, min(v), "slow query breakdown"))
            ret.append(MetricObject("mongodb.%s.avg" % k, average, "slow query breakdown"))

        return ret
