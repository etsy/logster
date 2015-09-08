#!/usr/bin/python

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


from time import time

class MetricObject(object):
    """General representation of a metric that can be used in many contexts"""
    def __init__(self, name, value, units='', type='float', timestamp=int(time()), metric_type='g'):
        self.name = name
        self.value = value
        self.units = units
        self.type = type
        self.timestamp = timestamp
        self.metric_type = metric_type

class LogsterParser(object):
    """Base class for logster parsers"""
    def parse_line(self, line):
        """Take a line and do any parsing we need to do. Required for parsers"""
        raise RuntimeError("Implement me!")

    def get_state(self, duration):
        """Run any calculations needed and return list of metric objects"""
        raise RuntimeError("Implement me!")


class LogsterParsingException(Exception):
    """Raise this exception if the parse_line function wants to
        throw a 'recoverable' exception - i.e. you want parsing
        to continue but want to skip this line and log a failure."""
    pass

class LockingError(Exception):
    """ Exception raised for errors creating or destroying lockfiles. """
    pass


class LogsterOutput(object):
    """ Base class for logster outputs"""
    def __init__(self, parser, options, logger):
        self.options = options
        self.logger = logger
        self.dry_run = options.dry_run

    def get_metric_name(self, metric, separator="."):
        """ Convenience method for contructing metric names
             Takes into account any supplied prefix/suffix options"""
        metric_name = metric.name
        if self.options.metric_prefix:
            metric_name = self.options.metric_prefix + separator + metric_name
        if self.options.metric_suffix:
            metric_name = metric_name + separator + self.options.metric_suffix
        return metric_name

    def submit(self, metrics):
        """Send metrics to the specific output"""
        raise RuntimeError("Implement me!")
