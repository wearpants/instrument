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

class StatsMetric(object):
    """Plot graphs of metrics.
    
    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output stats and
    plots using :func:`dump`. These are the only public methods.
    
    Each metric consumes one open file and 32K of memory while running.
    Dumping stats requires enough memory to load all data points for each
    metric.
    
    :cvar plots_dir: directory to save plots in. Defaults to `./statsplots`.
    :cvar dump_atexit: automatically :func:`dump` stats when the interpreter exits. Defaults to True.
    """

    plots_dir = os.path.abspath("statsplots") 
    dump_atexit = True 
    
    struct = struct.Struct('<Id')
    dtype = np.dtype([('count', np.uint32), ('elapsed', np.float64)])            
    lock = threading.Lock()
    table = None
    instances = {}

    if sys.version_info.major >= 3:
        mktemp = lambda self: tempfile.TemporaryFile(mode = 'w+b', buffering = 32768)
    else:
        # python2.7: argument name differs
        mktemp = lambda self: tempfile.TemporaryFile(mode = 'w+b', bufsize = 32768)
    
    def __init__(self, name):
        self.name = name
        self.temp = self.mktemp()
    
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
            
            shutil.rmtree(cls.plots_dir, ignore_errors=True)
            os.mkdir(cls.plots_dir)
            
            cls.table = prettytable.PrettyTable(['Name', 'Count Mean', 'Count Stddev', 'Elapsed Mean', 'Elapsed Stddev'])
            cls.table.set_style(prettytable.PLAIN_COLUMNS)
            cls.table.sortby = 'Name'
            cls.table.align['Name'] = 'l'
            cls.table.float_format = '.2'
            
            for self in cls.instances.values():
                self._dump()
            
            print(cls.table, file=sys.stderr)    
    
    def _dump(self):
        """dump data for an individual metric. For internal use only."""
        
        try:
            self.temp.seek(0) # seek to beginning            
            arr = np.fromfile(self.temp, self.dtype)
            
            count_arr = arr['count']
            elapsed_arr = arr['elapsed']
            
            count_mean = np.mean(count_arr)
            count_std = np.std(count_arr)
            elapsed_mean = np.mean(elapsed_arr)
            elapsed_std = np.std(elapsed_arr)
            
            # write to prettytable
            self.table.add_row([self.name, count_mean, count_std, elapsed_mean, elapsed_std])

            # plot things
            plt.figure(1, figsize = (8, 18))
            plt.subplot(3, 1, 1)
            self._histogram('count', count_mean, count_std, count_arr)
            plt.subplot(3, 1, 2)            
            self._histogram('elapsed', elapsed_mean, elapsed_std, elapsed_arr)
            plt.subplot(3, 1, 3)            
            self._scatter(count_arr, elapsed_arr)
            plt.savefig(os.path.join(self.plots_dir, ".".join((self.name, 'png'))),
                        bbox_inches="tight")

        finally:
            self.temp.close()
            plt.close()
    
    def _histogram(self, which, mu, sigma, data):
        """plot a histogram. For internal use only"""
        
        weights = np.ones_like(data)/len(data) # make bar heights sum to 100%
        n, bins, patches = plt.hist(data, bins=25, weights=weights, facecolor='blue', alpha=0.5)

        plt.title(r'%s %s: $\mu=%.2f$, $\sigma=%.2f$' % (self.name, which.capitalize(), mu, sigma))
        plt.xlabel('Items' if which == 'count' else 'Seconds')
        plt.ylabel('Frequency')
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, position: "{:.1f}%".format(y*100)))
        
    def _scatter(self, count_arr, elapsed_arr):
        """plot a scatter plot of count vs. elapsed. For internal use only"""

        plt.scatter(count_arr, elapsed_arr)
        plt.title('{}: Count vs. Elapsed'.format(self.name))
        plt.xlabel('Items')
        plt.ylabel('Seconds')
