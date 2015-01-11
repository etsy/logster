from logster.tailers import Tailer
import os


class LogtailTailer(Tailer):
    short_name = 'logtail'
    default_logtail_path = '/usr/sbin/logtail2'

    def __init__(self, *args):
        super(LogtailTailer, self).__init__(*args)
        self.shell_tail = "%s -f %s -o %s" % (self.options.logtail, self.logfile, self.statefile)

    def create_statefile(self):
        input = os.popen(self.shell_tail)
        retval = input.close()
        if not retval is None:
            self.logger.warning('%s returned bad exit code %s' % (self.shell_tail, retval))

    def ireadlines(self):
        input = os.popen(self.shell_tail)
        for line in input:
            yield line
        input.close()

