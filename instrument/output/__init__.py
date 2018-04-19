import sys

def _do_print(name, count, elapsed, file):
    if name is not None:
        print("%s: %d items in %.2f seconds"%(name, count, elapsed), file=file)
    else:
        print("%d items in %.2f seconds"%(count, elapsed), file=file)

def print_metric(name, count, elapsed):
    """A metric function that prints to standard output

    :arg str name: name of the metric
    :arg int count: number of items
    :arg float elapsed: time in seconds
    """
    _do_print(name, count, elapsed, file=sys.stdout)

def stderr_metric(name, count, elapsed):
    """A metric function that prints to standard error

    :arg str name: name of the metric
    :arg int count: number of items
    :arg float elapsed: time in seconds
    """
    _do_print(name, count, elapsed, file=sys.stderr)

def make_multi_metric(*metrics):
    """Make a new metric function that calls the supplied metrics

    :arg functions metrics: metric functions
    :rtype: function
    """
    def multi_metric(name, count, elapsed):
        """Calls multiple metrics (closure)"""
        for m in metrics:
            m(name, count, elapsed)
    return multi_metric
