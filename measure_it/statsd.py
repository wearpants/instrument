"""save metrics to `statsd <http://codeascraft.com/2011/02/15/measure-anything-measure-everything/>`__"""

from __future__ import print_function, division, absolute_import

try:
    from statsd.defaults.django import statsd
except Exception: # many possible errors, incl. ImportError & ImproperlyConfigured
    from statsd.defaults.env import statsd

def statsd_metric(name, count, elapsed):
    """Metric that records to statsd/graphite"""
    with statsd.pipeline() as pipe:
        pipe.incr(name, count)
        pipe.timing(name, int(round(1000 * elapsed)))  # milliseconds
