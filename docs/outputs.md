Supported Outputs
------------------

Logster supports output classes that can send metrics to a backend
service or data store. Backend services, for instance, can retain metrics in a
time series data store, visualize metrics in graphs or tables, or generate alerts
based on defined thresholds.

Logster includes the following built-in outputs:

* [Graphite][graphite] (`graphite`): An open-source
  time-series data store that provides visualization through a web-browser.
* [Ganglia][ganglia] (`ganglia`): A scalable distributed monitoring
  system for high-performance computing systems.
* [Amazon CloudWatch][cloudwatch] (`cloudwatch`): A monitoring service for AWS
  cloud resources and the applications you run on AWS.
* [Nagios][nagios] (`nsca`): An open-source monitoring system for systems,
  networks and infrastructure
* [StatsD][statsd] (`statsd`): A simple daemon for easy stats aggregation
* Standard Output (`stdout`): Outputs the metrics to stdout.

Outputs are just Python classes that implement the interface defined in [Output
Interface](./output_interface.md). Multiple outputs can be used at once: use the
`--output` (`-o`) commandline option repeatedly to specify the output classes
you'd like to use.


## Available Third-party outputs
- 

If you have an output you'd like to be included here, please open a pull
request with a link to its source/GitHub repo and a brief description of its
use.

Built-in outputs can be referenced using their short name (`graphite`, `ganglia`
etc). To use third-party outputs you must specify a fully-qualified module
and class name that's available on the [search path][search_path].

[graphite]: http://graphite.wikidot.com
[ganglia]: http://ganglia.info/
[cloudwatch]: https://aws.amazon.com/cloudwatch/
[nagios]: https://www.nagios.org/
[statsd]: https://github.com/etsy/statsd
[search_path]: https://docs.python.org/2/tutorial/modules.html#the-module-search-path
