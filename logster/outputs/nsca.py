from logster.logster_helper import LogsterOutput
import socket
import re
import os


class NSCAOutput(LogsterOutput):
    shortname = 'nsca'
    send_nsca = "/usr/sbin/send_nsca"


    @classmethod
    def add_options(cls, parser):
        parser.add_option('--nsca-host', action='store',
                           help='Hostname and port for NSCA daemon, e.g. nsca.example.com:5667')
        parser.add_option('--nsca-service-hostname', action='store',
                           help='<host_name> value to use in nsca passive service check. Default is \"%default\"',
                           default=socket.gethostname())


    def __init__(self, parser, options, logger):
        super(NSCAOutput, self).__init__(parser, options, logger)
        if not options.nsca_host:
            parser.print_help()
            parser.error("You must supply --nsca-host when using 'nsca' as an output type.")
        if (re.match("^[\w\.\-]+\:\d+$", options.nsca_host) is None):
            parser.print_help()
            parser.error("Invalid host:port found for NSCA: '%s'" % options.nsca_host)
        self.host = options.nsca_host.split(':')
        self.nsca_service_hostname = options.nsca_service_hostname

    def submit(self, metrics):

        for metric in metrics:
            metric_name = self.get_metric_name(metric, "_")

            metric_string = "\t".join((self.nsca_service_hostname, metric_name, str(metric.value), metric.units,))
            self.logger.debug("Submitting NSCA status: %s" % metric_string)

            nsca_cmd = "echo '%s' | %s -H %s -p %s" % (metric_string, NSCAOutput.send_nsca, self.host[0], self.host[1],)

            if (not self.dry_run):
                os.system(nsca_cmd)
            else:
                print("%s" % nsca_cmd)

