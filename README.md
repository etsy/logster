# Logster - generate metrics from logfiles [![Build Status](https://secure.travis-ci.org/etsy/logster.png)](http://travis-ci.org/etsy/logster)

Logster is a utility for reading log files and generating metrics in Graphite
or Ganglia or Amazon CloudWatch. It is ideal for visualizing trends of events that are occurring in
your application/system/error logs. For example, you might use logster to graph
the number of occurrences of HTTP response code that appears in your web server
logs.

Logster maintains a cursor, via logtail, on each log file that it reads so that
each successive execution only inspects new log entries. In other words, a 1
minute crontab entry for logster would allow you to generate near real-time
trends in Graphite or Ganglia or Amazon CloudWatch for anything you want to measure from your logs.

This tool is made up of a framework script, logster, and parsing scripts that
are written to accommodate your specific log format. Two sample parsers are
included in this distribution. The parser scripts essentially read a log file
line by line, apply a regular expression to extract useful data from the lines
you are interested in, and then aggregate that data into metrics that will be
submitted to Ganglia or Graphite or Amazon CloudWatch. Take a look through the sample
parsers, which should give you some idea of how to get started writing your
own.


## History

The logster project was created at Etsy as a fork of ganglia-logtailer
(https://bitbucket.org/maplebed/ganglia-logtailer). We made the decision to
fork ganglia-logtailer because we were removing daemon-mode from the original
framework. We only make use of cron-mode, and supporting both cron- and
daemon-modes makes for more work when creating parsing scripts. We care
strongly about simplicity in writing parsing scripts -- which enables more of
our engineers to write log parsers quickly.


## Installation

Logster depends on the "logtail" utility that can be obtained from the logcheck
package, either from a Debian package manager or from source:

    http://packages.debian.org/source/sid/logcheck

RPMs for logcheck can be found here:

    http://rpmfind.net/linux/rpm2html/search.php?query=logcheck

Once you have logtail installed via the logcheck package, you make want to look
over the actual logster script itself to adjust any paths necessary. Then the
only other thing you need to do is run the installation commands from the
`setup.py` file:

    $ sudo python setup.py install


## Usage

You can test logster from the command line. There are two sample parsers:
SampleLogster, which generates stats from an Apache access log; and
Log4jLogster, which generates stats from a log4j log. The --dry-run option will
allow you to see the metrics being generated on stdout rather than sending them
to Ganglia or Graphite or Amazon CloudWatch.

    $ sudo /usr/sbin/logster --dry-run --output=ganglia SampleLogster /var/log/httpd/access_log

    $ sudo /usr/sbin/logster --dry-run --output=graphite --graphite-host=graphite.example.com:2003 SampleLogster /var/log/httpd/access_log

You can use the provided parsers, or you can use your own parsers by passing
the complete module and parser name. In this case, the name of the parser does
not have to match the name of the module (you can have a logster.py file with a
MyCustomParser parser). Just make sure the module is in your Python path - via
a virtualenv, for example.

    $ /env/my_org/bin/logster --dry-run --output=stdout my_org_package.logster.MyCustomParser /var/log/my_custom_log

Additional usage details can be found with the -h option:

    $ ./logster -h
    usage: logster [options] parser logfile

    Tail a log file and filter each line to generate metrics that can be sent to
    common monitoring packages.

    Options:
      -h, --help            show this help message and exit
      -p METRIC_PREFIX, --metric-prefix=METRIC_PREFIX
                            Add prefix to all published metrics. This is for
                            people that may multiple instances of same service on
                            same host.
      -x METRIC_SUFFIX, --metric-suffix=METRIC_PREFIX
                            Add suffix to all published metrics. This is for
                            people that may multiple instances of same service on
                            same host.
      --parser-help         Print usage and options for the selected parser
      --parser-options=PARSER_OPTIONS
                            Options to pass to the logster parser such as "-o
                            VALUE --option2 VALUE". These are parser-specific and
                            passed directly to the parser.
      --gmetric-options=GMETRIC_OPTIONS
                            Options to pass to gmetric such as "-d 180 -c
                            /etc/ganglia/gmond.conf" (default). These are passed
                            directly to gmetric.
      --graphite-host=GRAPHITE_HOST
                            Hostname and port for Graphite collector, e.g.
                            graphite.example.com:2003
      --aws-key=AWS_KEY     Amazon credential key
      --aws-secret-key=AWS_SECRET_KEY
                            Amazon credential secret key
      -s STATE_DIR, --state-dir=STATE_DIR
                            Where to store the logtail state file.  Default
                            location /var/run
      -o OUTPUT, --output=OUTPUT
                            Where to send metrics (can specify multiple times).
                            Choices are 'graphite', 'ganglia', or 'stdout'.
      -d, --dry-run         Parse the log file but send stats to standard output.
      -D, --debug           Provide more verbose logging for debugging.
