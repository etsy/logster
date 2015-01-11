class Tailer(object):
    """ Base class for tailer implementations """
    def __init__(self, logfile, statefile, options, logger):
        self.logfile = logfile
        self.statefile = statefile
        self.options = options
        self.logger = logger

    def create_statefile(self):
        """ Create a statefile, with the offset of the end of the log file.
        Override if your tailer implementation can do this more efficiently
        """
        for _ in self.ireadlines():
            pass

    def ireadlines(self):
        """ Return a generator over lines in the logfile, updating the
        statefile when the generator is exhausted
        """
        raise NotImplementedError()
