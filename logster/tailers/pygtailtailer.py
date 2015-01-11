from logster.tailers import Tailer
import pygtail


class PygtailTailer(Tailer):
    short_name = 'pygtail'

    def ireadlines(self):
        tailer = pygtail.Pygtail(self.logfile, offset_file=self.statefile)
        for line in tailer:
            yield line
