"""plot metrics with matplotlib"""

import os.path
import shutil

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from ._numpy import NumpyMetric

__all__ = ['PlotMetric']

class PlotMetric(NumpyMetric):
    """Plot graphs of metrics. See :class:`NumpyMetric <._numpy.NumpyMetric>` for usage.

    :cvar outdir: directory to save plots in. Defaults to ``./instrument_plots``.
    """

    instances = {}
    outdir = os.path.abspath("instrument_plots")

    @classmethod
    def _pre_dump(cls):
        """Output all recorded stats"""
        shutil.rmtree(cls.outdir, ignore_errors=True)
        os.makedirs(cls.outdir)
        super(PlotMetric, cls)._pre_dump()

    def _cleanup(self):
        plt.clf()
        plt.close()
        super(PlotMetric, self)._cleanup()

    def _output(self):
        plt.figure(1, figsize = (8, 18))
        plt.subplot(3, 1, 1)
        self._histogram('count', self.count_mean, self.count_std, self.count_arr)
        plt.subplot(3, 1, 2)
        self._histogram('elapsed', self.elapsed_mean, self.elapsed_std, self.elapsed_arr)
        plt.subplot(3, 1, 3)
        self._scatter()
        plt.savefig(os.path.join(self.outdir, ".".join((self.name, 'png'))),
                    bbox_inches="tight")

        super(PlotMetric, self)._output()

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
