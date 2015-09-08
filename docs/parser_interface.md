Parser Interface
-----------------

Parser classes are responsible for processing incoming logs line-by-line, and
providing an aggregated list of metrics for submission to the configured
outputs.

A parser is required to implement at least the following methods:

* `parse_line(self, line)`: called once for each line found in the log since
  the last Logster run. Responsible for parsing the log line and extracting
  values that are aggregated later.

  Parameters: `line` is the log line string

  Raises: `logster.logster_helper.LogsterParsingException` when the current
  line cannot be parsed. Logster will continue with the next log line.

* `get_state(self, duration)`: called once for each Logster run. Returns an
  iterable of MetricObject instances with aggregated metrics values from the
  parsed log lines.

  Parameters: `duration` is the number of seconds since the last Logster run.
  Metrics values returned are usually expected to be averaged across the
  Logster run duration.

A base class is provided at [logster.logster_helper.LogsterParser][logster_parser].

[logster_parser]: ../logster/logster_helper.py
