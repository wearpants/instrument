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
            # time retrieving an element, and add to total elapsed
            t = time()
            try:
                count, x = next(it)
            finally:
                # increment in a try/finally s.t. if next() throws an exception,
                # we account for that time
                total_time += time() - t
            yield x
    finally:
        # we exit through here either with StopIteration or another exception
        metric(name, 
               count, total_time)
        
def measure_decorator(func, metric = print_metric, name = None):
    """Wrap a generator function in `measure`

    :arg function func: a function that produces a generator
    :arg function metric: f(name, count, total_time)
    :arg str name: a name for the stats. If None, derived from function name
    """
    def wrapper(*args, **kwargs):
        iterable = func(*args, **kwargs)
        return measure(iterable, metric, name if name is not None else
                         func.__module__ + '.' +func.__name__)

    return wrapper