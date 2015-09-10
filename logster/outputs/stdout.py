from logster.logster_helper import LogsterOutput


class StdoutOutput(LogsterOutput):
    shortname = 'stdout'


    @classmethod
    def add_options(cls, parser):
        parser.add_option('--stdout-separator', action='store', default="_", dest="stdout_separator",
                          help='Separator between prefix/suffix and name for stdout. Default is \"%default\".')


    def __init__(self, parser, options, logger):
        super(StdoutOutput, self).__init__(parser, options, logger)
        self.separator = options.stdout_separator


    def submit(self, metrics):
        for metric in metrics:
            metric_name = self.get_metric_name(metric, self.separator)
            print("%s %s %s" % (metric.timestamp, metric_name, metric.value))

