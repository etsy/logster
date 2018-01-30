#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
'''
Created on 16 jan 2018

@author: gbvbg
'''

import time
from datetime import datetime
from datetime import timedelta
import re
import optparse
import logging
from logster.logster_helper import MetricObject, LogsterParser


class Template():
    AAA = re.compile("^AAA")
    ZZZZ = re.compile("^ZZZZ")
    T0VAL = re.compile("^T0*(\\d+)")
    BBB = re.compile("BBB")
    TOP = re.compile("TOP")
    VALUE_LINE = re.compile("^[A-Z_0-9]+,T\\d{4},.+")
    SYMBOLS = re.compile("[\s\%\(\)-\/\.]")


def valid_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise optparse.OptionValueError(msg)


class NmonLogster(LogsterParser):
    host = ''
    headers = {}
    interval = ''
    dt = ''
    path1 = None
    time_shift = None
    serial_number = None
    mtm = None
    host = None
    nmon_startdate = None
    nmon_starttime = None
    snapshots = None
    all_snaps_readed = False
    have_finshed = False
    interval_seconds = None

    def __init__(self, option_string=None):
        if option_string:
            options = option_string.split(' ')
        else:
            options = []

        optparser = optparse.OptionParser(usage="usage: %prog [options] NmonLogster [parser_options] logfile",
                                          description="Tail a nmon file and generate metrics.")
        optparser.add_option('--roundTo', '-r', action='store',
                    type=int, default=None,
                    help='Specify interval to round timestamps. Default is None.')
        optparser.add_option('--startdate', '-s', action='store',
                    default=None,
                    help='Specvify start date.')

        opts, args = optparser.parse_args(args=options)
        self.roundTo = opts.roundTo
        self.startdate = None
        if opts.startdate is not None:
            self.startdate = datetime.strptime(opts.startdate, "%d.%m.%Y")
        self.path = ''
        self.metrics = []

    def parse_line(self, line):
        try:
            line = line.strip()
            if Template.AAA.match(line):
                tokens = line.split(',')
                if(tokens[1] == 'host'):
                    self.host = tokens[2]
                    ppath = "unspecified." + self.host + ".nmon"
                    self.path1 = (ppath if not self.path
                                  else self.path + "." + ppath)

                if(tokens[1] == 'SerialNumber'):
                    self.serial_number = tokens[2]

                if(tokens[1] == 'MachineType'):
                    self.mtm = tokens[3]
                    ppath = (self.mtm + "-" + self.serial_number
                             + "." + self.host + ".nmon")
                    self.path1 = (ppath if not self.path
                                  else self.path + "." + ppath)

                if(tokens[1] == 'date'):
                    self.nmon_startdate = datetime.strptime(tokens[2],
                                                            "%d-%b-%Y")

                if(tokens[1] == 'time'):
                    for f in ["%H:%M:%S", "%H:%M.%S"]:
                        try:
                            self.nmon_starttime = \
                                datetime.strptime(tokens[2], f)
                            break
                        except ValueError:
                            continue

                if(self.nmon_startdate is not None
                   or self.nmon_starttime is not None):
                    if(self.startdate is not None
                       and self.nmon_startdate is not None):
                        self.time_shift = self.startdate - self.nmon_startdate
                        if(self.nmon_starttime.hour > 14):
                            self.time_shift = self.time_shift - timedelta(days=1)

                if(tokens[1] == 'snapshots'):
                    self.snapshots = tokens[2]

                if (tokens[1] == 'interval'):
                    self.interval_seconds = tokens[2]

            elif Template.ZZZZ.match(line):
                tokens = line.split(',')
                self.interval = tokens[1]
                dt = time.strptime(tokens[3] + ' ' +
                                   tokens[2], "%d-%b-%Y %H:%M:%S")
                dt = datetime.fromtimestamp(time.mktime(dt))
                if (self.roundTo is not None):
                    dt = self.round_time(dt, self.roundTo)
                if (self.time_shift is not None):
                    dt = dt + self.time_shift
                self.dt = dt

                snapshot_number = Template.T0VAL.match(self.interval).group(1)
                if (snapshot_number == self.snapshots):
                    self.all_snaps_readed = True

            elif Template.VALUE_LINE.match(line):
                k = line.split(',')[0]
                self.read_nmon_line(line, k, self.headers[k],
                                    self.dt, self.path1)
            elif Template.BBB.match(line):
                pass
            else:
                h = self.make_header(line)
                self.headers[h[0]] = h
        except Exception:
            '''
            sys.stderr.write("WARNING: can'parse, the line is skiped: {}\n"
                             .format(line))
            traceback.print_exc(file=sys.stderr)
            '''
            logging.getLogger('logster').warn("can'parse, the line is skiped: {}"
                                              .format(line))

    def make_header(self, line):
        words = line.split(',')
        if (words[-1] == ""):
            words.pop()
        return list(
            map(lambda w:
                w.strip()
                .replace(' ', '_')
                .replace('-', '_')
                .replace('(', '_')
                .replace(')', '_')
                .replace('%', '_')
                .replace('/', '_')
                .replace('.', '_'),
                words)
            )

    def read_nmon_line(self, line, nmonSection, nmonHeader, dt, path):
        values = line.strip().split(',')
        values.remove

        if (len(values) != len(nmonHeader)):
            logging.getLogger('logster').warn("length of values:{} and headers:{} does not mismatch"
                  .format(len(values), len(nmonHeader)))

        limit = len(values)
        if(len(values) > len(nmonHeader)):
            limit = len(nmonHeader)

            logging.getLogger('logster').warn(
                "length of values:{} > headers:{} - line: {}"
                .format(len(values), len(nmonHeader), line))
            logging.getLogger('logster').warn(
                "Printing only {} values\n".format(limit))

        for i in range(2, limit):
            name = "%s.%s.%s" % (path, nmonSection,  nmonHeader[i])
            m = MetricObject(name, values[i], timestamp=time.mktime(dt.timetuple()))
            self.metrics += [m]

    def get_state(self, duration):
        return self.metrics

    def round_time(self, dt=None, roundTo=60):
        '''Round a datetime object to any time laps in seconds
        dt : datetime.datetime object, default now.
        roundTo : Closest number of seconds to round to, default 1 minute.
        Author: Thierry Husson 2012 - Use it as you want but don't blame me.
        '''
        if dt is None:
            dt = datetime.now()
        seconds = (dt - dt.min).seconds
        # // is a floor division, not a comment on following line:
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dt + timedelta(0, rounding-seconds, -dt.microsecond)
