import re
import optparse

from logster.logster_helper import MetricObject, LogsterParser, LogsterParsingException


class OccurrenceLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.occurrence = []
        self.pattern_list = []
        self.error_type = {}

        if option_string:
            options = option_string.split(' ')
        else:
            options = []

        optparser = optparse.OptionParser()
        optparser.add_option('--pattern-file', '-p', dest='pattern_file',
                            help='Path to file with pattern list. File struct: "pattern-name";"pattern";')
        optparser.add_option('--raw', action="store_true", dest='raw',
                            help='Send raw metric to graphite, do not take time duration into metric calculation')

        opts, args = optparser.parse_args(args=options)

        if opts.pattern_file:
            for line in open(opts.pattern_file):
                if len(line.strip()) > 0:
                    pattern_line = self.read_pattern_line(line)
                    self.pattern_list.append([pattern_line[0], re.compile(pattern_line[1], flags=re.IGNORECASE)])
        else:
            optparser.error('File with patterns not given')

        self.raw_data = opts.raw

    def read_pattern_line(self, line):
        line_split = line.split(" : ")
        return [self.remove_quotation_marks(line_split[0]), self.remove_quotation_marks(line_split[1])]

    def remove_quotation_marks(self, word):
        return word.replace("\"", "").strip()

    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        for pattern in self.pattern_list:
            try:
                search = pattern[1].search(line)
                if search:
                    self.error_type.update({pattern[0]: self.error_type.get(pattern[0], 0)+1})
            except Exception as e:
                raise LogsterParsingException("Pattern search failed with %s" % e)

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = float(duration)

        # Return a list of metrics objects
        result = []
        for key, occ in self.error_type.iteritems():
            if self.raw_data:
                metric = MetricObject(key, occ, "Responses")
            else:
                metric = MetricObject(key, (occ / self.duration), "Responses per sec")
            result.append(metric)
        return result
