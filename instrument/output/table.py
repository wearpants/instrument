"""print pretty tables of statistics"""
import prettytable
import sys

from ._numpy import NumpyMetric

__all__ = ['TableMetric']

class TableMetric(NumpyMetric):
    """Print a table of statistics. See :class:`NumpyMetric <._numpy.NumpyMetric>` for usage.

    :cvar outfile: output file. Defaults to ``sys.stderr``.
    """
    instances = {}
    outfile = sys.stderr

    @classmethod
    def _pre_dump(cls):
        cls.table = prettytable.PrettyTable(['Name', 'Count Mean', 'Count Stddev', 'Elapsed Mean', 'Elapsed Stddev'])
        cls.table.set_style(prettytable.PLAIN_COLUMNS)
        cls.table.sortby = 'Name'
        cls.table.align['Name'] = 'l'
        cls.table.float_format = '.2'
        super(TableMetric, cls)._pre_dump()

    @classmethod
    def _post_dump(cls):
        print(cls.table, file=cls.outfile)
        super(TableMetric, cls)._post_dump()

    def _output(self):
        # write to prettytable
        self.table.add_row([self.name, self.count_mean, self.count_std, self.elapsed_mean, self.elapsed_std])
        super(TableMetric, self)._output()

