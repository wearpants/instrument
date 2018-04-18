"""save metrics to standard library logging"""

from __future__ import print_function, division, absolute_import

import logging

def make_log_metric(level=logging.INFO, msg="%d elements in %.2f seconds"):
    """Make a new metric function that logs at the given level

    :arg int level: logging level, defaults to `logging.INFO`
    :arg string msg: logging message format string, taking `count` and `elapsed`
    :rtype: function
    """
    def log_metric(name, count, elapsed):
        log_name = 'instrument.{}'.format(name) if name else 'instrument'
        logging.getLogger(log_name).log(level, msg, count, elapsed)
    return log_metric

log_metric = make_log_metric()
