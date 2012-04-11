import time
import re

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

# For help with what this is all about, see one of the sample
# Logster parsers which have more detailed comments about
# the structure of the class and each method's function.

# Collect arbitrary metric lines and spit out aggregated
# metric values (MetricObjects) based on the metric names
# found in the lines. Any conforming metric, one parser. Sweet.

class MetricLogster(LogsterParser):

    def __init__(self, option_string=None):
        self.metrics = {}
        # Examples:
        #
        # Mar 30 20:35:03 mail1 whatever[1323]: metric=mail1.my.metric value=9
        # Mar 31 03:44:28 fs9 blah[9403]: metric=foo.bar value=4484884
        #
        self.reg = re.compile('.+ metric=(?P<metricname>[-_a-zA-Z0-9.]+) value=(?P<value>[0-9.]+))')

    def parse_line(self, line):
        try:
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                metric = str(linebits['metricname'])
                value = int(linebits['value'])
                if self.metrics.has_key(metric):
                    self.metrics[metric] = self.metrics[metric] + int(value)
                else:
                    self.metrics[metric] = int(value)
            else:
                raise LogsterParsingException, "regmatch failed to match"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        self.duration = duration

        outlines = []

        for k in self.metrics.keys():
            outlines.append(MetricObject(k, (self.metrics[k] / self.duration), "per sec"))

        return outlines
