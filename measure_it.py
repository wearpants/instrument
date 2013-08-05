from time import time
from functools import wraps

# if your metric function throws an exception or is slow, you suck.

def print_metric(name, count, elapsed):
    if name is not None:
        print("%s: %d elements in %f seconds"%(name, count, elapsed))
    else:
        print("%d elements in %f seconds"%(count, elapsed))

def measure(iterable, metric = print_metric, name = None):
    """Record count and time statistics for consuming an iterable

    :arg iterable: an iterable thing
    :arg function metric: f(name, count, total_time)
    :arg str name: a name for the stats.
    """
    total_time = 0
    count = 0
    it = enumerate(iterable, 1) # count, element
    try:
        while True:
            # time retrieving an element, and add to total elapsed. In a
            # try/finally s.t. if next() throws an exception, we account for
            # that time
            t = time()
            try:
                count, x = next(it)
            finally:
                total_time += time() - t
            yield x
    finally:
        # underlying iterable is exhausted (StopIteration) or errored. Record
        # the `metric` and allow exception to propogate
        metric(name, count, total_time)

def _measure_decorate(metric = print_metric, name = None):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            iterable = func(*args, **kwargs)
            return measure(iterable, metric, name if name is not None
                           else func.__module__ + '.' +func.__name__)
        
        return wrapped
    return wrapper

measure.func = _measure_decorate

def measure_each(iterable, metric = print_metric, name = None):
    """Record count and time statistics for each item of an iterable

    :arg iterable: an iterable thing
    :arg function metric: f(name, 1, time)
    :arg str name: a name for the stats.
    """
    it = iter(iterable)
    while True:
        # time retrieving an element.
        t = time()
        try:
            x = next(it)
        except StopIteration:
            # don't record a metric for final next() call
            raise
        except Exception:
            # record a metric for other exceptions, than raise
            metric(name, 1, time() - t)
            raise
        else:
            # normal path, record metric and yield
            metric(name, 1, time() - t)
            yield x
        
def _measure_each_decorate(metric = print_metric, name = None):
    def wrapper(func):        
        @wraps(func)        
        def wrapped(*args, **kwargs):
            iterable = func(*args, **kwargs)
            return measure_each(iterable, metric, name if name is not None
                           else func.__module__ + '.' +func.__name__)
        
        return wrapped
    return wrapper

measure_each.func = _measure_each_decorate

try:
    from statsd import statsd, StatsClient
    if statsd is None: statsd = StatsClient()
except ImportError:
    pass
else:
    def statsd_metric(name, count, elapsed):
        with statsd.pipeline as pipe:
            pipe.incr(name, count)
            pipe.timing(name, int(round(1000 * dt)))  # Convert to ms.