from logster.outputs.stdout import StdoutOutput
from logster.outputs.graphite import GraphiteOutput
from logster.outputs.ganglia import GangliaOutput
from logster.outputs.statsd import StatsdOutput
from logster.outputs.cloudwatch import CloudwatchOutput
from logster.outputs.nsca import NSCAOutput

builtin_output_classes = (
        StdoutOutput,
        GraphiteOutput,
        GangliaOutput,
        StatsdOutput,
        CloudwatchOutput,
        NSCAOutput,
)

builtin_outputs = dict([(a.shortname, a) for a in builtin_output_classes])
