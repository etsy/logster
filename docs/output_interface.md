Output Interface
-----------------

Output classes are responsible for submitting metrics gathered in a
Logster run to a specific output. Each output class should implement
at least the following method:

* `submit(self, metrics)`: the submit method is invoked at the end of
  each run, and is responsible for sending the collected metrics values
  to the output backend.

  The `metrics` parameter is an iterable of [MetricObject][metric_object]
  objects.

There's a base class provided at [logster.logster_helper.LogsterOutput][logster_output].
If your output class extends LogsterOutput, it needs to provide an implementation
for the `submit` method and will get access to the [get_metric_name][logster_output]
function for generating metric names using supplied prefix/suffix options.


Optionally, an output class can override the constructor:

* `__init__(self, parser, options, logger)`: The output is instantiated
  before invoking the parser on new log lines.

  Parameters: `parser` is the optparse.OptionParser instance, `options`
  are the parsed optparse options, `logger` is the python logging instance

If your ouput needs to take custom options on the commandline, it can implement
the `add_options` classmethod to add its own options to an optparse.OptionParser
instance:

* `add_options(cls, parser)`: Called during optparse option parsing to add custom
  commandline options for this output.

  Parameters: `parser` is teh optparse.OptionParser instance.


[metric_object]: ../logster/logster_helper.py
[logster_output]: ../logster/logster_helper.py
