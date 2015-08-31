from logster.logster_helper import LogsterOutput
import os


class GangliaOutput(LogsterOutput):
    shortname = 'ganglia'
    gmetric = "/usr/bin/gmetric"

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--gmetric-options', action='store',
            help='Options to pass to gmetric such as "-d 180 -c /etc/ganglia/gmond.conf" (default). These are passed directly to gmetric.',
            default='-d 180 -c /etc/ganglia/gmond.conf')


    def __init__(self, parser, options, logger):
        super(GangliaOutput, self).__init__(parser, options, logger)
        self.gmetric_options = options.gmetric_options


    def submit(self, metrics):
        for metric in metrics:
             metric_name = self.get_metric_name(metric, "_")

             gmetric_cmd = "%s %s --name %s --value %s --type %s --units \"%s\"" % ( GangliaOutput.gmetric, self.gmetric_options, metric_name, metric.value, metric.type, metric.units)
             self.logger.debug("Submitting Ganglia metric: %s" % gmetric_cmd)

             if (not self.dry_run):
                 os.system("%s" % gmetric_cmd)
             else:
                 print("%s" % gmetric_cmd)

