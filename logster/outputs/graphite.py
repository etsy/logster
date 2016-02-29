from logster.logster_helper import LogsterOutput
import re
import socket


class GraphiteOutput(LogsterOutput):
    shortname = 'graphite'


    @classmethod
    def add_options(cls, parser):
        parser.add_option('--graphite-host', action='store',
                           help='Hostname and port for Graphite collector, e.g. graphite.example.com:2003')
        parser.add_option('--graphite-protocol', action='store', default='tcp',
                           choices=('tcp', 'udp'),
                           help='Specify graphite socket protocol. Options are tcp and udp. Defaults to tcp.')


    def __init__(self, parser, options, logger):
        super(GraphiteOutput, self).__init__(parser, options, logger)
        if not options.graphite_host:
            parser.print_help()
            parser.error("You must supply --graphite-host when using 'graphite' as an output type.")
        if (re.match("^[\w\.\-]+\:\d+$", options.graphite_host) == None):
            parser.print_help()
            parser.error("Invalid host:port found for Graphite: '%s'" % options.graphite_host)

        self.graphite_host = options.graphite_host
        self.graphite_protocol = options.graphite_protocol


    def submit(self, metrics):

        if (not self.dry_run):
            host = self.graphite_host.split(':')

            if self.graphite_protocol == 'udp':
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect((host[0], int(host[1])))

        try:
            for metric in metrics:
                metric_name = self.get_metric_name(metric)

                # Spaces in graphite metric names will cause failure
                if ' ' in metric_name:
                    self.logger.error('Invalid metric name, spaces not allowed')
                    return

                metric_string = "%s %s %s" % (metric_name, metric.value, metric.timestamp)
                self.logger.debug("Submitting Graphite metric: %s" % metric_string)

                if (not self.dry_run):
                    s.sendall(("%s\n" % metric_string).encode('ascii'))
                else:
                    print("%s %s" % (self.graphite_host, metric_string))
        finally:
            if (not self.dry_run):
                s.close()
