from __future__ import print_function, division, absolute_import

import struct
import tempfile
import warnings
import os.path
import shutil
import sys
import threading
import atexit

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import prettytable

class NumpyMetric(object):
    """Base class for numpy-based metrics

    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output stats and
    using :func:`dump`. These are the only public methods.

    Each metric consumes one open file and 32K of memory while running.
    Dumping stats requires enough memory to load all data points for each
    metric.

    :cvar dump_atexit: automatically :func:`dump` stats when the interpreter exits. Defaults to True.
    """

    dump_atexit = True

    struct = struct.Struct('<Id')
    dtype = np.dtype([('count', np.uint32), ('elapsed', np.float64)])
    lock = threading.Lock()
    instances = {}

    if sys.version_info.major >= 3:
        mktemp = lambda self: tempfile.TemporaryFile(mode = 'w+b', buffering = 32768)
    else:
        # python2.7: argument name differs
        mktemp = lambda self: tempfile.TemporaryFile(mode = 'w+b', bufsize = 32768)

    def __init__(self, name):
        self.name = name
        self.temp = self.mktemp()
        self.count_arr = None
        self.elapsed_arr = None

    @classmethod
    def metric(cls, name, count, elapsed):
        """A metric function that generates plots and stats

        :arg str name: name of the metric
        :arg int count: number of elements
        :arg float elapsed: time in seconds
        """

        if name is None:
            warnings.warn("Ignoring unnamed metric", stacklevel=3)
            return

        with cls.lock:
            # register with atexit on first call
            if cls.dump_atexit and not cls.instances:
                atexit.register(cls.dump)

            try:
                self = cls.instances[name]
            except KeyError:
                self = cls.instances[name] = cls(name)

            self.temp.write(self.struct.pack(count, elapsed))

    @classmethod
    def dump(cls):
        """Output all recorded stats"""
        with cls.lock:
            if not cls.instances: return
            if cls.dump_atexit and sys.version_info.major >= 3:
                # python2.7 has no unregister function
                atexit.unregister(cls.dump)

            cls._pre_dump()

            for self in cls.instances.values():
                self._dump()

            cls._post_dump()

    def _dump(self):
        """dump data for an individual metric. For internal use only."""

        try:
            self.temp.seek(0) # seek to beginning
            arr = np.fromfile(self.temp, self.dtype)
            self.count_arr = arr['count']
            self.elapsed_arr = arr['elapsed']
            self._output()
        finally:
            self.temp.close()
            self._cleanup()


    @classmethod
    def _pre_dump(cls):
        pass

    @classmethod
    def _post_dump(cls):
        pass

    def _output(self):
        pass

    def _cleanup(self):
        pass


class StatsTableMetric(NumpyMetric):
    """Print a table of statistics


    :cvar outfile: output file. Defaults to `sys.stderr`.
    """
    outfile = sys.stderr
    table = None

    @classmethod
    def _pre_dump(cls):
        cls.table = prettytable.PrettyTable(['Name', 'Count Mean', 'Count Stddev', 'Elapsed Mean', 'Elapsed Stddev'])
        cls.table.set_style(prettytable.PLAIN_COLUMNS)
        cls.table.sortby = 'Name'
        cls.table.align['Name'] = 'l'
        cls.table.float_format = '.2'
        super(StatsTableMetric, cls)._pre_dump()

    @classmethod
    def _post_dump(cls):
        print(cls.table, file=cls.outfile)
        super(StatsTableMetric, cls)._post_dump()

    def _output(self):
        count_mean = np.mean(self.count_arr)
        count_std = np.std(self.count_arr)
        elapsed_mean = np.mean(self.elapsed_arr)
        elapsed_std = np.std(self.elapsed_arr)

        # write to prettytable
        self.table.add_row([self.name, count_mean, count_std, elapsed_mean, elapsed_std])
        super(StatsTableMetric, self)._output()

class MatplotlibMetric(NumpyMetric):
    """Plot graphs of metrics.

    :cvar plots_dir: directory to save plots in. Defaults to `./statsplots`.
    """
    plots_dir = os.path.abspath("statsplots")

    @classmethod
    def _pre_dump(cls):
        """Output all recorded stats"""
        shutil.rmtree(cls.plots_dir, ignore_errors=True)
        os.mkdir(cls.plots_dir)
        super(MatplotlibMetric, cls)._pre_dump()

    @classmethod
    def _post_dump(cls):
        plt.close()
        super(MatplotlibMetric, cls)._post_dump()

    def _output(self):
        """dump data for an individual metric. For internal use only."""
        count_mean = np.mean(self.count_arr)
        count_std = np.std(self.count_arr)
        elapsed_mean = np.mean(self.elapsed_arr)
        elapsed_std = np.std(self.elapsed_arr)

        # plot things
        plt.figure(1, figsize = (8, 18))
        plt.subplot(3, 1, 1)
        self._histogram('count', count_mean, count_std, self.count_arr)
        plt.subplot(3, 1, 2)
        self._histogram('elapsed', elapsed_mean, elapsed_std, self.elapsed_arr)
        plt.subplot(3, 1, 3)
        self._scatter()
        plt.savefig(os.path.join(self.plots_dir, ".".join((self.name, 'png'))),
                    bbox_inches="tight")

        super(MatplotlibMetric, self)._output()

    def _histogram(self, which, mu, sigma, data):
        """plot a histogram. For internal use only"""

        weights = np.ones_like(data)/len(data) # make bar heights sum to 100%
        n, bins, patches = plt.hist(data, bins=25, weights=weights, facecolor='blue', alpha=0.5)

        plt.title(r'%s %s: $\mu=%.2f$, $\sigma=%.2f$' % (self.name, which.capitalize(), mu, sigma))
        plt.xlabel('Items' if which == 'count' else 'Seconds')
        plt.ylabel('Frequency')
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, position: "{:.1f}%".format(y*100)))

    def _scatter(self):
        """plot a scatter plot of count vs. elapsed. For internal use only"""

        plt.scatter(self.count_arr, self.elapsed_arr)
        plt.title('{}: Count vs. Elapsed'.format(self.name))
        plt.xlabel('Items')
        plt.ylabel('Seconds')