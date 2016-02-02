# Logster - generate metrics from logfiles [![Build Status](https://secure.travis-ci.org/etsy/logster.svg)](http://travis-ci.org/etsy/logster)

Logster is a utility for reading log files and generating metrics to
configurable outputs. It is ideal for visualizing trends of events that
are occurring in your application/system/error logs. For example, you might use
logster to graph the number of occurrences of HTTP response code that appears in
your web server logs.

Logster maintains a cursor, via a tailer, on each log file that it reads so that
each successive execution only inspects new log entries. In other words, a 1
minute crontab entry for logster would allow you to generate near real-time
trends in the configured output for anything you want to measure from your logs.

This tool is made up of a framework script, logster, and parsing classes that
are written to accommodate your specific log format. Sample parsers are
included in this distribution. The parser classes essentially read a log file
line by line, apply a regular expression to extract useful data from the lines
you are interested in, and then aggregate that data into metrics that will be
submitted to the configured output. The sample parsers should give you some idea
of how to get started writing your own. A list of available parsers can be
found on the [Parsers](./docs/parsers.md) page.

Graphite, Ganglia, Amazon CloudWatch, Nagios, StatsD and stdout outputs are
provided, and Logster also supports the use of third-party output classes.
A list of available output classes can be found on the [Outputs](./docs/outputs.md)
page.


## History

The logster project was created at Etsy as a fork of ganglia-logtailer
(https://bitbucket.org/maplebed/ganglia-logtailer). We made the decision to
fork ganglia-logtailer because we were removing daemon-mode from the original
framework. We only make use of cron-mode, and supporting both cron- and
daemon-modes makes for more work when creating parsing scripts. We care
strongly about simplicity in writing parsing scripts -- which enables more of
our engineers to write log parsers quickly.


## Installation

Logster supports two methods for gathering data from a logfile:

1. By default, Logster uses the "logtail" utility that can be obtained from the
   logcheck package, either from a Debian package manager or from source:

       http://packages.debian.org/source/sid/logcheck

   RPMs for logcheck can be found here:

       http://rpmfind.net/linux/rpm2html/search.php?query=logcheck

2. Optionally, Logster can use the "Pygtail" Python module instead of logtail.
   You can install Pygtail using pip

   ```
   $ pip install pygtail
   ```

   To use Pygtail, supply the ```--tailer=pygtail``` option on the Logster
   commandline.

Also, Logster supports two methods for locking files (which it has to do):

1. By default, Logster uses ```fcntl.flock```.

2. Optionally, Logster can use the "Portalocker" Python module instead of fcntl
   (which is not available on Windows). You can install Portalocker using pip,
   similar to Pygtail above.

   To use Portalocker, supply the ```--locker=portalocker``` option on the
   Logster commandline.


Once you have logtail or Pygtail installed, install Logster using the `setup.py` file:

    $ sudo python setup.py install


## Usage

You can test logster from the command line.  The --dry-run option will
allow you to see the metrics being generated on stdout rather than sending them
to your configured output.

    $ sudo /usr/bin/logster --dry-run --output=ganglia SampleLogster /var/log/httpd/access_log

    $ sudo /usr/bin/logster --dry-run --output=graphite --graphite-host=graphite.example.com:2003 SampleLogster /var/log/httpd/access_log

You can use the provided parsers, or you can use your own parsers by passing
the complete module and parser name. In this case, the name of the parser does
not have to match the name of the module (you can have a logster.py file with a
MyCustomParser parser). Just make sure the module is in your Python path - via
a virtualenv, for example.

    $ /env/my_org/bin/logster --dry-run --output=stdout my_org_package.logster.MyCustomParser /var/log/my_custom_log

Additional usage details can be found with the -h option:

    $ logster -h
    Usage: logster [options] parser logfile

    Tail a log file and filter each line to generate metrics that can be sent to
    common monitoring packages.

    Options:
      -h, --help            show this help message and exit
      -t TAILER, --tailer=TAILER
                            Specify which tailer to use. Options are logtail and
                            pygtail. Default is "logtail".
      --logtail=LOGTAIL     Specify location of logtail. Default
                            "/usr/sbin/logtail2"
      -p METRIC_PREFIX, --metric-prefix=METRIC_PREFIX
                            Add prefix to all published metrics. This is for
                            people that may multiple instances of same service on
                            same host.
      -x METRIC_SUFFIX, --metric-suffix=METRIC_SUFFIX
                            Add suffix to all published metrics. This is for
                            people that may add suffix at the end of their
                            metrics.
      --parser-help         Print usage and options for the selected parser
      --parser-options=PARSER_OPTIONS
                            Options to pass to the logster parser such as "-o
                            VALUE --option2 VALUE". These are parser-specific and
                            passed directly to the parser.
      -s STATE_DIR, --state-dir=STATE_DIR
                            Where to store the tailer state file.  Default
                            location /var/run
      -l LOG_DIR, --log-dir=LOG_DIR
                            Where to store the logster logfile.  Default location
                            /var/log/logster
      --log-conf=LOG_CONF   Logging configuration file. None by default
      -o OUTPUT, --output=OUTPUT
                            Where to send metrics (can specify multiple times).
                            Choices are statsd, stdout, cloudwatch, graphite,
                            ganglia, nsca or a fully qualified Python class name
      -d, --dry-run         Parse the log file but send stats to standard output.
      -D, --debug           Provide more verbose logging for debugging.


## Contributing

- Fork the project
- Add your feature
- If you are adding new functionality, document it in the README
- Verify your code by running the test suite, and adding additional tests if able.
- Push the branch up to GitHub (bonus points for topic branches)
- Send a pull request to the etsy/logster project.

If you have questions, you can find us on IRC in the `#codeascraft` channel on Freenode.

