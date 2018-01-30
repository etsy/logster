#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

###
###  logster
###
###  Tails a log and applies a log parser (that knows what to do with specific)
###  types of entries in the log, then reports metrics to Ganglia and/or Graphite.
###
###  Usage:
###
###    $ logster [options] parser logfile
###
###  Help:
###
###    $ logster -h
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
###  Forked from the ganglia-logtailer project
###  (http://bitbucket.org/maplebed/ganglia-logtailer):
###    Copyright Linden Research, Inc. 2008
###    Released under the GPL v2 or later.
###    For a full description of the license, please visit
###    http://www.gnu.org/licenses/gpl.txt
###

import os
import sys
import optparse
import stat
import logging.handlers
import logging.config
import traceback
import platform
import inspect
import pickle

from time import time
from math import floor

# Local dependencies
from logster.logster_helper import LogsterParsingException, LockingError, LogsterOutput
from logster.tailers.logtailtailer import LogtailTailer
from logster.outputs.builtin import builtin_outputs


class Options:
    log_dir = '/var/log/logster'
    state_dir = '/var/run'


options = Options()
lock_exception_klass = None


# optparse callback to locate output class by shortname or full path
def load_output_klass(option, opt, value, parser):
    outputs = getattr(parser.values, option.dest) if getattr(parser.values, option.dest) else []

    output_klass = builtin_outputs.get(value)
    if not output_klass:
        # Assume full path if shortname not found in builtin outputs
        try:
            module_name, output_name = value.rsplit('.', 1)
            module = __import__(module_name, globals(), locals(), [output_name])
            output_klass = getattr(module, output_name)
        except:
            parser.error("Unable to load output class %s" % value)

    # Ignore dupes
    if output_klass not in outputs:
        # Add output class-specific optparse options
        add_options = getattr(output_klass, "add_options", None)
        if callable(add_options):
            option_group = optparse.OptionGroup(parser, "%s options" % output_klass.__name__)
            add_options(option_group)
            parser.add_option_group(option_group)

        outputs.append(output_klass)

    # Append to list of outputs (option can be specified multiple times)
    setattr(parser.values, option.dest, outputs)


# As we add options during parse, their defaults don't get picked up
# (optionparser evaluates defaults once at the start of parse_args)
# This re-evaluates defaults after the parse and sets any missing
def parse_args(optionparser):
    options, arguments = optionparser.parse_args()
    post_parse_defaults = optionparser.get_default_values()
    for option in optionparser._get_all_options():
        if option.dest:
            has_default = hasattr(post_parse_defaults, option.dest)
            has_option_val = hasattr(options, option.dest)
            if has_default and not has_option_val:
                setattr(options, option.dest,
                        getattr(post_parse_defaults, option.dest))

    return options, arguments


def parse_cmdline():
    global options
    global lock_exception_klass
    # Command-line options and parsing.
    cmdline = optparse.OptionParser(usage="usage: %prog [options] parser logfile",
        description="Tail a log file and filter each line to generate metrics that can be sent to common monitoring packages.")
    cmdline.add_option('--tailer', '-t', action='store', default='logtail',
                        choices=('logtail', 'pygtail'), help='Specify which tailer to use. Options are logtail and pygtail. Default is \"%default\".')
    cmdline.add_option('--locker', action='store', default='fcntl',
                        choices=('fcntl', 'portalocker'), help='Specify which file locker to use. Options are fcntl and portalocker. Default is \"%default\".')
    cmdline.add_option('--logtail', action='store', default=LogtailTailer.default_logtail_path,
                        help='Specify location of logtail. Default \"%default\"')
    cmdline.add_option('--metric-prefix', '-p', action='store',
                        help='Add prefix to all published metrics. This is for people that may multiple instances of same service on same host.',
                        default='')
    cmdline.add_option('--metric-suffix', '-x', action='store',
                        help='Add suffix to all published metrics. This is for people that may add suffix at the end of their metrics.',
                        default=None)
    cmdline.add_option('--parser-help', action='store_true',
                        help='Print usage and options for the selected parser')
    cmdline.add_option('--parser-options', action='store',
                        help='Options to pass to the logster parser such as "-o VALUE --option2 VALUE". These are parser-specific and passed directly to the parser.')
    cmdline.add_option('--state-dir', '-s', action='store', default=options.state_dir,
                        help='Where to store the tailer state file.  Default location %s' % options.state_dir)
    cmdline.add_option('--log-dir', '-l', action='store', default=options.log_dir,
                        help='Where to store the logster logfile.  Default location %s' % options.log_dir)
    cmdline.add_option('--log-conf', action='store', default=None,
                        help='Logging configuration file. None by default')
    cmdline.add_option('--output', '-o', action='callback', callback=load_output_klass, type="string", dest="output", metavar="OUTPUT",
                       help="Where to send metrics (can specify multiple times).\
                             Choices are %s or a fully qualified Python class name" % ', '.join(builtin_outputs.keys()))
    cmdline.add_option('--dry-run', '-d', action='store_true', default=False,
                        help='Parse the log file but send stats to standard output.')
    cmdline.add_option('--debug', '-D', action='store_true', default=False,
                        help='Provide more verbose logging for debugging.')
    options, arguments = parse_args(cmdline)

    if options.parser_help:
        options.parser_options = '-h'

    if (len(arguments) != 2):
        cmdline.print_help()
        cmdline.error("Supply at least two arguments: parser and logfile.")

    if options.tailer == 'pygtail':
        from logster.tailers.pygtailtailer import PygtailTailer
        tailer_klass = PygtailTailer
    else:
        tailer_klass = LogtailTailer

    if options.locker == 'portalocker':
        locker_module = __import__('portalocker')
        lock_exception_klass = getattr(locker_module, 'LockException')
    else:
        locker_module = __import__('fcntl')
        lock_exception_klass = getattr(locker_module, 'IOError')

    if not (hasattr(options, 'output') and len(options.output) > 0):
        cmdline.print_help()
        cmdline.error("Supply where the data should be sent with -o (or --output).")

    parser_klass_name = arguments[0]
    if parser_klass_name.find('.') == -1:
        # If it's a single name, find it in the base logster package
        parser_klass_name = 'logster.parsers.%s.%s' % (parser_klass_name, parser_klass_name)
    options.log_file = arguments[1]

    # Logging infrastructure for use throughout the script.
    # Uses appending log file, rotated at 100 MB, keeping 5.
    if (not os.path.isdir(options.log_dir)):
        os.mkdir(options.log_dir)
    logger = logging.getLogger('logster')
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    hdlr = logging.handlers.RotatingFileHandler('%s/logster.log' % options.log_dir,
                                                 'a', 100 * 1024 * 1024, 5)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    if (options.log_conf):
        logging.config.fileConfig(options.log_conf)

    if (options.debug):
        logger.setLevel(logging.DEBUG)

    if (not os.path.isdir(options.state_dir)):
        os.mkdir(options.state_dir)

    options.tailer_klass = tailer_klass
    options.parser_klass_name = parser_klass_name
    options.logger = logger

    return cmdline
## This provides a lineno() function to make it easy to grab the line
## number that we're on (for logging)
## Danny Yoo (dyoo@hkn.eecs.berkeley.edu)
## taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/145297
import inspect


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def submit_stats(parser, duration, outputs):
    metrics = parser.get_state(duration)
    for output in outputs:
        output.submit(metrics)


def start_locking(lockfile_name):
    global lock_exception_klass
    """ Acquire a lock via a provided lockfile filename. """
    if os.path.exists(lockfile_name):
        raise LockingError("Lock file (%s) already exists." % lockfile_name)

    f = open(lockfile_name, 'w')

    try:
        if options.locker == 'portalocker':
            locker_module = __import__('portalocker')
            lock_EX = getattr(locker_module, 'LOCK_EX')
            lock_NB = getattr(locker_module, 'LOCK_NB')
            lock_method = getattr(locker_module, 'lock')
            lock_method(f, lock_EX | lock_NB)
        else:
            locker_module = __import__('fcntl')
            lock_EX = getattr(locker_module, 'LOCK_EX')
            lock_NB = getattr(locker_module, 'LOCK_NB')
            lock_method = getattr(locker_module, 'flock')
            lock_method(f, lock_EX | lock_NB)
        f.write("%s" % os.getpid())
    except lock_exception_klass:
        # Would be better to also check the pid in the lock file and remove the
        # lock file if that pid no longer exists in the process table.
        raise LockingError("Cannot acquire logster lock (%s)" % lockfile_name)

    logging.getLogger('logster').debug("Locking successful")
    return f


def end_locking(lockfile_fd, lockfile_name):
    global lock_exception_klass
    """ Release a lock via a provided file descriptor. """
    try:
        if options.locker == 'portalocker':
            locker_module = __import__( 'portalocker' )
            lock_klass = getattr(locker_module, 'portalocker')
            unlock_method = getattr(locker_module, 'unlock')
            unlock_method(lockfile_fd)
            #portalocker.unlock(lockfile_fd) # uses fcntl.LOCK_UN on posix (in contrast with the flock()ing below)
        else:
            locker_module = __import__('fcntl')
            lock_UN = getattr(locker_module, 'LOCK_UN')
            lock_NB = getattr(locker_module, 'LOCK_NB')
            lock_method = getattr(locker_module, 'flock')
            if platform.system() == "SunOS": # GH issue #17
                lock_method(lockfile_fd, lock_UN)
            else:
                lock_method(lockfile_fd, lock_UN | lock_NB)
    except lock_exception_klass:
        raise LockingError("Cannot release logster lock (%s)" % lockfile_name)

    try:
        lockfile_fd.close()
        os.unlink(lockfile_name)
    except OSError as e:
        raise LockingError("Cannot unlink %s" % lockfile_name)

    logging.getLogger('logster').debug("Unlocking successful")
    return


def main():
    script_start_time = time()
    cmdline = parse_cmdline()
    dirsafe_logfile = options.log_file.replace(os.sep,'-')
    state_file = ('%s' + os.sep + '%s-%s%s.state') % (options.state_dir,
                                       options.tailer_klass.short_name,
                                       options.parser_klass_name, dirsafe_logfile)
    lock_file = ('%s' + os.sep + '%s-%s%s.lock') % (options.state_dir,
                                      options.tailer_klass.short_name,
                                      options.parser_klass_name, dirsafe_logfile)
    tailer = options.tailer_klass(options.log_file, state_file,
                                  options, options.logger)
    nmon_file = ('%s' + os.sep + '%s-%s.pickle') % (options.state_dir,
                                       options.parser_klass_name, dirsafe_logfile)

    options.logger.info("Executing parser %s on logfile %s" % (
        options.parser_klass_name,
        options.log_file))
    options.logger.debug("Using state file %s" % state_file)

    # Import and instantiate the class from the module passed in.
    module_name, parser_name = options.parser_klass_name.rsplit('.', 1)
    module = __import__(module_name, globals(), locals(), [parser_name])
    parser = getattr(module, parser_name)(option_string=options.parser_options)

    # Instantiate output classes
    outputs = [output_klass(cmdline, options, options.logger) for output_klass in options.output]

    # Check for lock file so we don't run multiple copies of the same parser
    # simultaneuosly. This will happen if the log parsing takes more time than
    # the cron period.
    try:
        lockfile = start_locking(lock_file)
    except LockingError as e:
        options.logger.warning(str(e))
        sys.exit(1)

    # Get input to parse.
    try:

        # Read the age of the state file to see how long it's been since we last
        # ran. Replace the state file if it has gone missing. While we are here,
        # touch the state file to reset the time in case the tailer doesn't
        # find any new lines (and thus won't update the statefile).
        try:
            duration = 0
            state_file_age = os.stat(state_file)[stat.ST_MTIME]

            # Calculate now() - state file age to determine check duration.
            duration = floor(time()) - floor(state_file_age)
            options.logger.debug("Setting duration to %s seconds." % duration)

        except OSError as e:
            if options.parser_klass_name == 'logster.parsers.NmonLogster.NmonLogster':
                pass
            else:
                options.logger.info('Writing new state file and exiting. (Was either first run, or state file went missing.)')
                tailer.create_statefile()
                end_locking(lockfile, lock_file)
                sys.exit(0)

        # Parse each line from input, then send all stats to their collectors.
        if options.parser_klass_name == 'logster.parsers.NmonLogster.NmonLogster':
            if os.path.exists(nmon_file):
                with open(nmon_file, 'rb') as nmon_fh:
                    parser = pickle.load(nmon_fh)

        for line in tailer.ireadlines():
            try:
                parser.parse_line(line)
            except LogsterParsingException as e:
                # This should only catch recoverable exceptions (of which there
                # aren't any at the moment).
                options.logger.debug("Parsing exception caught at %s: %s" % (lineno(), e))

        submit_stats(parser, duration, outputs)

        if options.parser_klass_name == 'logster.parsers.NmonLogster.NmonLogster':
            parser.metrics = []
            with open(nmon_file, 'wb') as nmon_fh:
                pickle.dump(parser, nmon_fh)

    except SystemExit as e:
        raise
    except Exception as e:
        print("Exception caught at %s: %s" % (lineno(), e))
        traceback.print_exc()
        end_locking(lockfile, lock_file)
        sys.exit(1)

    # Log the execution time
    exec_time = round(time() - script_start_time, 1)
    options.logger.info("Total execution time: %s seconds." % exec_time)

    # Set mtime and atime for the state file to the startup time of the script
    # so that the cron interval is not thrown off by parsing a large number of
    # log entries.
    os.utime(state_file, (floor(script_start_time), floor(script_start_time)))

    end_locking(lockfile, lock_file)

    # try and remove the lockfile one last time, but it's a valid state that it's already been removed.
    try:
        end_locking(lockfile, lock_file)
    except Exception as e:
        pass

if __name__ == '__main__':
    main()

