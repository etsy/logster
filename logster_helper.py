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

class GangliaLogster(object):
    pass

class GraphiteLogster(object):
    pass

class GangliaMetricObject(object):
    def __init__(self, name, value, units='', type='float', tmax=60):
        self.name = name
        self.value = value
        self.units = units
        self.type = type
        self.tmax = tmax

class GraphiteMetricObject(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.timestamp = int(time())

class LogsterParsingException(Exception):
    """Raise this exception if the parse_line function wants to
        throw a 'recoverable' exception - i.e. you want parsing
        to continue but want to skip this line and log a failure."""
    pass

class LockingError(Exception):
    """ Exception raised for errors creating or destroying lockfiles. """
    def __init__(self, message):
        self.message = message


