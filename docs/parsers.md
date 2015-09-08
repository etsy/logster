Supported Parsers
------------------

Logster uses parsing classes that are written to accommodate your specific log
format. Sample parsers are included in this distribution.

Parser classes essentially read a log file line by line, apply a regular
expression to extract useful data from the lines you are interested in, and then
aggregate that data into metrics that will be submitted to the configured outputs.

The sample parsers should give you some idea of how to get started writing your own.

Logster includes the following built-in parsers:

* [ErrorLogLogster][errorloglogster]: count the number of different messages in an Apache error_log
* [JsonLogster][jsonlogster]: parses a file of Json objects, each on their own line
* [Log4jLogster][log4jlogster]: count the number of events for each log level in a log4j log
* [MetricLogster][metriclogster]: collects arbitrary metric lines and spits out aggregated
  metric values
* [PostfixLogster][postfixlogster]: count the number of sent/deferred/bounced emails from a
  [Postfix][postfix] log
* [SquidLogster][squidlogster]: count the number of responses and object size in the [squid][squid]
  access.log
* [SampleLogster][samplelogster]: count the number of response codes found in an Apache access
  log

You can use the provided parsers, or you can use your own parsers by passing
the complete module and parser name. In this case, the name of the parser does
not have to match the name of the module (you can have a logster.py file with a
MyCustomParser parser). Just make sure the module is in your [Python path][search_path]
via a virtualenv, for example.

    $ /env/my_org/bin/logster --dry-run --output=stdout my_org_package.logster.MyCustomParser /var/log/my_custom_log

Parsers are just Python classes that implement the interface defined in [Parser
Interface](./parser_interface.md).

## Available Third-party parsers
- 

If you have a parser you'd like to be included here, please open a pull
request with a link to its source/GitHub repo and a brief description of its
use.


[search_path]: https://docs.python.org/2/tutorial/modules.html#the-module-search-path
[errorloglogster]: ../logster/parsers/ErrorLogLogster.py
[jsonlogster]: ../logster/parsers/JsonLogster.py
[log4jlogster]: ../logster/parsers/Log4jLogster.py
[metriclogster]: ../logster/parsers/MetricLogster.py
[postfixlogster]: ../logster/parsers/PostfixLogster.py
[squidlogster]: ../logster/parsers/SquidLogster.py
[samplelogster]: ../logster/parsers/SampleLogster.py
[squid]: http://www.squid-cache.org/
[postfix]: http://www.postfix.org/
