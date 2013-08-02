from time import time

def print_metric(name, count, total_time):
    if name is not None:
        print("%s: %d elements in %f seconds"%(name, count, total_time))
    else:
        print("%d elements in %f seconds"%(count, total_time))

def measure(iterable, metric = print_metric, name = None):
    """Record count and time statistics for an iterable

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
        def wrapped(*args, **kwargs):
            iterable = func(*args, **kwargs)
            return measure(iterable, metric, name if name is not None
                           else func.__module__ + '.' +func.__name__)
        
        return wrapped
    return wrapper

measure.func = _measure_decorate