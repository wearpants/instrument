"""save metrics to `statsd <http://codeascraft.com/2011/02/15/measure-anything-measure-everything/>`__"""

from __future__ import print_function, division, absolute_import

from statsd import statsd, StatsClient
if statsd is None: statsd = StatsClient()

def statsd_metric(name, count, elapsed):
    """Metric that records to statsd/graphite"""
    with statsd.pipeline() as pipe:
        pipe.incr(name, count)
        pipe.timing(name, int(round(1000 * elapsed)))  # milliseconds