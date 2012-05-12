###  Author: Mark Crossfield <mark.crossfield@tradermedia.co.uk>, Mark Crossfield <mark@markcrossfield.co.uk>
###  Rewritten and extended in collaboration with Jeff Blaine, who first contributed the MetricLogster. 
###
###  Collects arbitrary metric lines and spits out aggregated
###  metric values (MetricObjects) based on the metric names
###  found in the lines. Any conforming metric, one parser. Sweet.
###  The logger indicates whether metric is a count or time by use of a marker.
###  This is enough information to work out what to push to Graphite;
###    - for counters the values are totalled
###    - for times the median and 90th percentile (configurable) are computed 
###
###  Logs should contain lines such as below - these can be interleaved with other lines with no problems.
###
###    ... METRIC_TIME metric=some.metric.time value=10ms
###    ... METRIC_TIME metric=some.metric.time value=11ms
###    ... METRIC_TIME metric=some.metric.time value=20ms
###    ... METRIC_COUNT metric=some.metric.count value=1
###    ... METRIC_COUNT metric=some.metric.count value=2.2
###
###  Results:
###    some.metric.count 3.2
###    some.metric.time.mean 13.6666666667
###    some.metric.time.median 11
###    some.metric.time.90th_percentile 18.2
###
###  For example:
###  sudo ./logster --output=stdout MetricLogster /var/log/example_app/app.log --parser-options '--percentiles 25,75,90'
###
###  Based on SampleLogster which is Copyright 2011, Etsy, Inc.

import re
import stats_helper
import optparse

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

class MetricLogster(LogsterParser):
    
    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        
        self.counts = {}
        self.times = {}
        
        if option_string:
            options = option_string.split(' ')
        else:
            options = []
        
        optparser = optparse.OptionParser()
        optparser.add_option('--percentiles', '-p', dest='percentiles', default='90',
                            help='Comma-separated list of percentiles to track: (default: "90")')
        optparser.add_option('--time-unit', '-t', dest='time_unit', default='ms',
                            help='The units of time to look for and record (default: "ms")')
        
        opts, args = optparser.parse_args(args=options)
        
        self.percentiles = opts.percentiles.split(',')
        self.time_unit = opts.time_unit
        
        # General regular expressions, expecting the metric name to be included in the log file.

        self.count_reg = re.compile('.*METRIC_COUNT\smetric=(?P<count_name>[^\s]+)\s+value=(?P<count_value>[0-9.]+)[^0-9.].*')
        self.time_reg = re.compile('.*METRIC_TIME\smetric=(?P<time_name>[^\s]+)\s+value=(?P<time_value>[0-9.]+)[^0-9.].*')
        
    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''
        
        try:
            count_match = self.count_reg.match(line)
            if count_match:
                countbits = count_match.groupdict()
                count_name = countbits['count_name']
                if not self.counts.has_key(count_name):
                    self.counts[count_name] = 0
                self.counts[count_name] += float(countbits['count_value']);
            
            time_match = self.time_reg.match(line)
            if time_match:
                time_name = time_match.groupdict()['time_name']
                if not self.times.has_key(time_name):
                    self.times[time_name] = [];
                self.times[time_name].append(int(time_match.groupdict()['time_value']))
            
        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e
            
    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        metrics = []
        if duration > 0:
            metrics += [MetricObject(counter, self.counts[counter]/duration) for counter in self.counts]
        for time_name in self.times:
            metrics.append(MetricObject(time_name+".mean", stats_helper.find_mean(self.times[time_name]), self.time_unit))
            metrics.append(MetricObject(time_name+".median", stats_helper.find_median(self.times[time_name]), self.time_unit))
            metrics += [MetricObject("%s.%sth_percentile" % (time_name,percentile), stats_helper.find_percentile(self.times[time_name],int(percentile)), self.time_unit) for percentile in self.percentiles]
                
        return metrics
