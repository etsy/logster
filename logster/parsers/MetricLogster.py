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
###  If the metric is a time the parser will extract the unit from the fist line it encounters for each run.
###  This means it is important for the logger to be consistent with its units.
###  Note: units are irrelevant for Graphite, as it does not support them; this functionality is to cater for Ganglia.
###
###  For example:
###  sudo ./logster --output=stdout MetricLogster /var/log/example_app/app.log --parser-options '--percentiles 25,75,90'
###
###  Based on SampleLogster which is Copyright 2011, Etsy, Inc.

import re
import optparse

from logster.parsers import stats_helper

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

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
                            help='Comma-separated list of integer percentiles to track: (default: "90")')

        opts, args = optparser.parse_args(args=options)

        self.percentiles = opts.percentiles.split(',')

        # General regular expressions, expecting the metric name to be included in the log file.

        self.count_reg = re.compile('.*METRIC_COUNT\smetric=(?P<count_name>[^\s]+)\s+value=(?P<count_value>[0-9.]+)[^0-9.].*')
        self.time_reg = re.compile('.*METRIC_TIME\smetric=(?P<time_name>[^\s]+)\s+value=(?P<time_value>[0-9.]+)\s*(?P<time_unit>[^\s$]*).*')

    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        count_match = self.count_reg.match(line)
        if count_match:
            countbits = count_match.groupdict()
            count_name = countbits['count_name']
            if count_name not in self.counts:
                self.counts[count_name] = 0.0
            self.counts[count_name] += float(countbits['count_value']);

        time_match = self.time_reg.match(line)
        if time_match:
            time_name = time_match.groupdict()['time_name']
            if time_name not in self.times:
                unit = time_match.groupdict()['time_unit']
                self.times[time_name] = {'unit': unit, 'values': []};
            self.times[time_name]['values'].append(float(time_match.groupdict()['time_value']))

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        duration = float(duration)
        metrics = []
        if duration > 0:
            metrics += [MetricObject(counter, self.counts[counter]/duration) for counter in self.counts]
        for time_name in self.times:
            values = self.times[time_name]['values']
            unit = self.times[time_name]['unit']
            metrics.append(MetricObject(time_name+'.mean', stats_helper.find_mean(values), unit))
            metrics.append(MetricObject(time_name+'.median', stats_helper.find_median(values), unit))
            metrics += [MetricObject('%s.%sth_percentile' % (time_name,percentile), stats_helper.find_percentile(values,int(percentile)), unit) for percentile in self.percentiles]

        return metrics
